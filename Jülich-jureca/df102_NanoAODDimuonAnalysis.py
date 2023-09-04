import ROOT
from dask_jobqueue import SLURMCluster
from dask.distributed import Client, performance_report
import argparse
import time
import csv
import subprocess
import os
import yaml
import requests
import prometheus_client

# Enable multi-threading
ROOT.ROOT.EnableImplicitMT()

# Point RDataFrame calls to Dask RDataFrame object
RDataFrame = ROOT.RDF.Experimental.Distributed.Dask.RDataFrame

# Define constants
QUEUE_NAME = 'dc-cpu'
LOGS_DIR = "logs"
DaskDashboardPort = 1243
LOCAL_DIRECTORY = '/tmp'
PROMETHEUS_CONFIG_PATH = '/p/project/cslfse/boulis1/prometheus/prometheus.yml'
CREATE_SCREEN_COMMAND = "/p/project/cslfse/boulis1/run_screen_script.sh"
EXEC_SCRIPT_PATH = '/p/project/cslfse/boulis1/exec_df102.sh'
ACOUNT_NAME = 'slfse'


def setup_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cores", type=int, default=1)
    parser.add_argument("-N", "--Nodes", type=int, default=1)
    parser.add_argument("-nf", "--nfiles", type=int, default=1)
    parser.add_argument("-nt", "--ntests", type=int, default=1)
    return parser.parse_args()

def create_connection(args):
    """
    Setup connection to a remote Slurm managed cluster using SSHCluster.
    """
    time = "10:00:00"
    job_name = f"distrdf_test_{args.cores}"
    output = f"{LOGS_DIR}/distrdf_test_{args.cores}_%j.out"
    error = f"{LOGS_DIR}/distrdf_test_{args.cores}_%j.err"

    cluster = SLURMCluster(
        memory='{}g'.format(4 * args.cores),
        processes=args.cores,
        account=ACOUNT_NAME,
        cores=args.cores,
        queue=QUEUE_NAME,
        local_directory=LOCAL_DIRECTORY,
        header_skip=['-n 1'],
        job_extra=['--ntasks-per-node=1', f'--time={time}', f'--job-name={job_name}', f'--output={output}', f'--error={error}'],
        job_script_prologue=[f'bash {EXEC_SCRIPT_PATH}'],
        scheduler_options={'dashboard_address': f':{DaskDashboardPort}'}
    )

    cluster.scale(jobs=args.Nodes)

    client = Client(cluster)

    client.wait_for_workers(n_workers=args.Nodes)

    return client

def createDataset(num_files):
    dataset = [ 'Run2012BC_DoubleMuParked_Muons.root' ] + [ 'Run2012BC_DoubleMuParked_Muons.root'.format(i) for i in range(1, num_files) ]
    return dataset

def write_runtime_to_csv(csv_name,runtime, num_cores):
    with open(csv_name, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([num_cores, runtime])

def write_txt(file_name, txt, mode):
    with open(file_name, mode) as file:
        file.write(txt)

def run(dataset, npartitions, client, args):
    # Create dataframe from NanoAOD files
    df = RDataFrame("Events", dataset, npartitions=npartitions, daskclient=client)

    #df = ROOT.RDataFrame("Events", "root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/Run2012BC_DoubleMuParked_Muons.root", npartitions=npartitions, daskclient=client)

    # For simplicity, select only events with exactly two muons and require opposite charge
    df_2mu = df.Filter("nMuon == 2", "Events with exactly two muons")
    df_os = df_2mu.Filter("Muon_charge[0] != Muon_charge[1]", "Muons with opposite charge")

    # Compute invariant mass of the dimuon system
    df_mass = df_os.Define("Dimuon_mass", "InvariantMass(Muon_pt, Muon_eta, Muon_phi, Muon_mass)")

    # Make histogram of dimuon mass spectrum
    h = df_mass.Histo1D(("Dimuon_mass", "Dimuon_mass", 30000, 0.25, 300), "Dimuon_mass")

    # Produce plot
    ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetTextFont(42)
    c = ROOT.TCanvas("c", "", 800, 700)
    c.SetLogx(); c.SetLogy()

    watch = ROOT.TStopwatch()
    h.SetTitle("")
    elapsed = watch.RealTime()

    h.GetXaxis().SetTitle("m_{#mu#mu} (GeV)"); h.GetXaxis().SetTitleSize(0.04)
    h.GetYaxis().SetTitle("N_{Events}"); h.GetYaxis().SetTitleSize(0.04)
    h.Draw()

    label = ROOT.TLatex(); label.SetNDC(True)
    label.DrawLatex(0.175, 0.740, "#eta")
    label.DrawLatex(0.205, 0.775, "#rho,#omega")
    label.DrawLatex(0.270, 0.740, "#phi")
    label.DrawLatex(0.400, 0.800, "J/#psi")
    label.DrawLatex(0.415, 0.670, "#psi'")
    label.DrawLatex(0.485, 0.700, "Y(1,2,3S)")
    label.DrawLatex(0.755, 0.680, "Z")
    label.SetTextSize(0.040); label.DrawLatex(0.100, 0.920, "#bf{CMS Open Data}")
    label.SetTextSize(0.030); label.DrawLatex(0.630, 0.920, "#sqrt{s} = 8 TeV, L_{int} = 11.6 fb^{-1}")

    c.SaveAs("dimuon_spectrum.pdf")
    write_runtime_to_csv('runtimes_df102_release_1.csv',elapsed, args.cores * args.Nodes)

def update_prometheus_config(target_endpoints):
    # Read existing YAML configuration from the file
    with open(PROMETHEUS_CONFIG_PATH, 'r') as config_file:
        config_content = config_file.read()

    config_dict = yaml.safe_load(config_content)
    config_dict['scrape_configs'][0]['static_configs'][0]['targets'] = target_endpoints

    updated_config_content = yaml.dump(config_dict, default_flow_style=False)

    with open(PROMETHEUS_CONFIG_PATH, 'w') as config_file:
        config_file.write(updated_config_content)

    prometheus_config_url = "http://localhost:9090/-/reload"  # Replace with your Prometheus host and port

    try:
        response = requests.post(prometheus_config_url)
        if response.status_code == 200:
            print("Prometheus configuration reloaded successfully.")
        else:
            print("Failed to reload Prometheus configuration.")
    except requests.exceptions.RequestException as e:
        print("Error reloading Prometheus configuration:", e)

def main():

    args = setup_arg_parser()

    # Create the connection to the remote Slurm managed cluster
    connection = create_connection(args)


    scheduler_address = connection.scheduler.address
    print("Dashboard Link: ",connection.dashboard_link)
    print(f"Dask Scheduler Address: {scheduler_address}")
    write_txt('endpoints.txt',connection.dashboard_link+'\n','w')

    # Get the worker information, including CPU metrics
    workers_info = connection.scheduler_info()["workers"]

    while len(workers_info) < (args.cores * args.Nodes) :
        workers_info = connection.scheduler_info()["workers"]
        print(f"Waiting for {args.cores * args.Nodes} workers...")
        time.sleep(5)

    target_endpoints = [f"localhost:{DaskDashboardPort}"]

    unique_addresses = set()  # Use a set to store unique addresses

    for worker, info in workers_info.items():
        port = info["services"]["dashboard"]
        address = worker.split("//")[1].split(":")[0]
        target_endpoints.append(f"{address}:{port}")
        # Check if the address is already in the set, and only add it if it's not
        if address not in unique_addresses:
                target_endpoints.append(f"{address}:9100")
                target_endpoints.append(f"{address}:8080")
                # Add the address to the set to track it as a unique entry
                unique_addresses.add(address)

    print(target_endpoints)
    write_txt('endpoints.txt','\n'.join(target_endpoints),'a')

    subprocess.run(['chmod', '+x', CREATE_SCREEN_COMMAND])
    subprocess.run(CREATE_SCREEN_COMMAND, shell=True, check=True)

    update_prometheus_config(target_endpoints)

    subprocess.run(['chmod', '+x', EXEC_SCRIPT_PATH])
    subprocess.run([EXEC_SCRIPT_PATH], shell=True, check=True)

    npartitions_per_core = 1
    ncores_total = args.cores * args.Nodes
    npartitions = ncores_total * npartitions_per_core
    nfiles = args.nfiles # 500
    ntests = args.ntests # 3

    dataset = createDataset(nfiles)
    files = [ os.path.join(LOCAL_DIRECTORY, data_file) for data_file in dataset ]

    for _ in range(ntests):
        with performance_report(filename="dask-report.html"):
            run(files, npartitions, connection, args)

    connection.close()

if __name__ == "__main__":
    main()
