import json
import pandas as pd
import numpy as np

def load_files(path):
    dfs = []
    for i in range(30):
        df = pd.read_csv(path+str(i+1)+'.csv')
        dfs.append(df)
    return dfs

def load_eb_output(path):
    df = pd.read_csv(path)
    return df

def get_avg_mem(dfs):
    avg_mem = []
    for df in dfs:
        avg = df['USED_MEMORY'].mean()
        avg_mem.append(avg)
    return  sum(avg_mem) / len(avg_mem)

def get_avg_eb(eb):
    avg_energy = eb['joule'].mean()
    avg_time = eb['time'].mean()
    return avg_energy, avg_time

def calc_component_score(scores, higher_is_better=False):
    minimum = min(scores)
    maximum = max(scores)
    diff = maximum - minimum
    if higher_is_better:
        scoresdist = [((x-minimum)/(diff/3))-1 for x in scores]
    else:
        scoresdist = [((maximum-x)/(diff/3))-1 for x in scores]
    return scoresdist

def get_avgs():
    pyarrowpathmeas = './results-sse-csv/pyarrow-test-'
    pyarrowpatheb = './results-sse-csv/pyarrow.csv'
    pyarrowdfs = load_files(pyarrowpathmeas)
    pyarrow_eb = load_eb_output(pyarrowpatheb)
    avg_mem_pyarrow = get_avg_mem(pyarrowdfs)
    avg_energy_pyarrow, avg_time_pyarrow = get_avg_eb(pyarrow_eb)

    numpypathmeas = './results-sse-csv/numpy-test-'
    numpypatheb = './results-sse-csv/numpy.csv'
    numpydfs = load_files(numpypathmeas)
    numpy_eb = load_eb_output(numpypatheb)
    avg_mem_numpy = get_avg_mem(numpydfs)
    avg_energy_numpy, avg_time_numpy = get_avg_eb(numpy_eb)

    pandaspathmeas = './results-sse-csv/pandas-test-'
    pandaspatheb = './results-sse-csv/pandas.csv'
    pandasdfs = load_files(pandaspathmeas)
    pandas_eb = load_eb_output(pandaspatheb)
    avg_mem_pandas = get_avg_mem(pandasdfs)
    avg_energy_pandas, avg_time_pandas = get_avg_eb(pandas_eb)

    avg_mem = [avg_mem_pyarrow, avg_mem_numpy, avg_mem_pandas]
    avg_energy = [avg_energy_pyarrow, avg_energy_numpy, avg_energy_pandas]
    avg_time = [avg_time_pyarrow, avg_time_numpy, avg_time_pandas]

    return avg_mem, avg_energy, avg_time

def get_code_metrics(lib_names, json_path):
    with open(json_path) as json_file:
        code_metrics = json.load(json_file)
    
    abstractness = [code_metrics[lib]['abstractness'] for lib in lib_names]
    instability = [code_metrics[lib]['instability'] for lib in lib_names]
    merged_prs = [code_metrics[lib]['merged_prs'] for lib in lib_names]
    closed_issues = [code_metrics[lib]['closed_issues'] for lib in lib_names]
    vulnerabilities = [
        code_metrics[lib]['crit_vulns'] 
        + 0.5*code_metrics[lib]['high_vulns'] 
        + 0.25*code_metrics[lib]['medium_vulns'] 
        + 0.2*code_metrics[lib]['low_vulns'] for lib in lib_names
    ]
    return abstractness, instability, merged_prs, closed_issues, vulnerabilities

def calc_score(lib_names, scores, weights):
    num_libs = len(lib_names)
    num_metrics = len(scores)
    nutris = {}
    for i in range(num_libs):
        lib_scores = [scores[j][i] for j in range(num_metrics)]
        avg = sum([lib_scores[j] * weights[j] for j in range(num_metrics)])/sum(weights)
        nutri = np.select(
            [avg < -0.4,
            (avg >= -0.4) & (avg < 0.2),
            (avg >= 0.2) & (avg < 0.8),
            (avg >= 0.8) & (avg < 1.4),
            avg > 1.4],
            ["E", "D", "C", "B", "A"],
            ""
        )
        nutris[lib_names[i]] = nutri[()]
    print(nutris)
    return nutris

def create_nutris():
    lib_names = ["pyarrow", "numpy", "pandas"]
    scores_mem, scores_energy, scores_time = get_avgs()
    abst, inst, prs, issues, vulns = get_code_metrics(lib_names, "github-metrics.json")

    mem = calc_component_score(scores_mem)
    energy = calc_component_score(scores_energy)
    time = calc_component_score(scores_time)
    abstractness = calc_component_score(abst, higher_is_better=True)
    instability = calc_component_score(inst)
    merged_prs = calc_component_score(prs, higher_is_better=True)
    closed_issues = calc_component_score(issues, higher_is_better=True)
    vulnerabilities = calc_component_score(vulns)
    
    metrics_to_include = [
        mem,
        energy,
        time,
        abstractness,
        instability,
        merged_prs,
        closed_issues,
        vulnerabilities
    ]

    return calc_score(lib_names, metrics_to_include, [1 for _ in metrics_to_include])

print(create_nutris())
