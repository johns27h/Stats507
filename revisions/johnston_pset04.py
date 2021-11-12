# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.12.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Heather Johnston
# ### Stats 507, Problem Set 4
# ### Fall 2021

# -----------------------------------------------------------------------------
import pandas as pd
import numpy as np
from itertools import product
from scipy.stats import norm, beta, chisquare, ttest_ind
from IPython.core.display import display, HTML
# Note to self: figure out matplotlib import conflict
# import matplotlib.pyplot as plt

# # Question 0: Topic in Pandas
#
# ## Stack and Unstack
# * Stack and Unstack are similar to "melt" and "pivot" methods for transforming data
# * R users may be familiar with "pivot_wider" and "pivot_longer" (formerly "spread" and "gather")
# * Stack transforms column names to new index and values to column
#
# ## Example: Stack
# * Consider the `example` DataFrame below to be measurements of some value taken on different days at different times.
# * It would be natural to want these to be "gathered" into long format, which we can do using `stack`

example = pd.DataFrame({"day":["Monday", "Wednesday", "Friday"],
                        "morning":[4, 5, 6],
                        "afternoon":[8, 9, 0]})
example.set_index("day", inplace=True)
print(example)
print(example.stack())

# ## Example: Unstack
# * Conversely, for displaying data, it's often handy to have it in a wider format
# * Unstack is especially convenient after using `groupby` on a dataframe

rng = np.random.default_rng(100)
long_data = pd.DataFrame({"group":["a", "a", "a", "a", "b", "b", "b", "b"],
                          "program":["x", "y", "x", "y", "x", "y", "x", "y"],
                         "score":rng.integers(0, 100, 8),
                         "value":rng.integers(0, 20, 8)
                         })
long_data.groupby(["group", "program"]).mean()
long_data.groupby(["group", "program"]).mean().unstack()

# # Question 1: NHANES Table
#
# See Appendix for modified Q3 from Pset 2. 

# -----------------------------------------------------------------------------
# Part a: including gender
data = pd.read_pickle("nhanes_demographic.pkl")

# For part b, I used this StackOverflow response to create a new variable
# https://stackoverflow.com/questions/48027171/create-a-variable-in-a-pandas-dataframe-based-on-information-in-the-dataframe

# +
# -----------------------------------------------------------------------------
# Part b: Merging ODESTS
# Note that I renamed "ODESTS" to be "dentition_status" when I made the pickle
teeth = pd.read_pickle("nhanes_teeth.pkl")
teeth["respondent_id"] = teeth["respondent_id"].astype(str)
teeth_ds = teeth[["respondent_id", "dentition_status"]]
data2 = data.merge(teeth_ds, how = "left", on = "respondent_id")

new_names = {"respondent_id":"id",
             "status":"exam_status",
            "dentition_status":"ohx_status"}
data2.rename(columns=new_names, inplace=True)
data2["under_20"] = data2["age"].copy().apply(lambda x: x < 20)

def get_val(row):
    college = ['Some college or AA degree', 'College graduate or above']
    if row.educ_level == 'High school graduate / GED' or row.under_20:
        return "No college/<20"
    elif row.educ_level in college:
        return "some college/college graduate"
    else:
        return np.nan
data2["college"] = data2.apply(get_val, axis = 1)

data2 = data2[["id", "gender", "age", "under_20", 
               "college", "exam_status", "ohx_status"]]

def get_val_exam(row):
    status = ["Interviewed and examined", "Complete"]
    if row.exam_status == status[0] and row.ohx_status == status[1]:
        return "complete"
    else:
        return "missing"
data2["ohx"] = data2.apply(get_val_exam, axis = 1)
# -

# -----------------------------------------------------------------------------
# Part c: Removing where exam_status != "Interviewed and examined"
data3 = data2.loc[data2["exam_status"] == "Interviewed and examined", ].copy()
print(str(data2.shape[0] - data3.shape[0]) + " observations removed")
print(str(data3.shape[0]) + " observations remaining")

# +
# -----------------------------------------------------------------------------
# Part d: Table with ohx and age, under_20, gender, college
results_under_20 = data3.groupby(["under_20", "ohx"]).size().unstack()
under_20_p = chisquare(results_under_20.values, axis=0).pvalue
results_under_20["P-value"] = under_20_p[0]
results_gender = data3.groupby(["gender", "ohx"]).size().unstack()
gender_p = chisquare(results_gender.values, axis=0).pvalue
results_gender["P-value"] = gender_p[0]
results_college = data3.groupby(["college", "ohx"]).size().unstack()
college_p = chisquare(results_college.values, axis=0).pvalue
results_college["P-value"] = college_p[0]
results_age = data3.groupby(["ohx"]).age.agg([np.mean, np.std]).transpose()
results_age["P-value"] = 2*[ttest_ind(
    data3.loc[data3["ohx"]=="complete", "age"], 
    data3.loc[data3["ohx"]=="missing", "age"])[1]]

results_under_20["variable"] = "Under 20?"
results_gender["variable"] = "Gender"
results_college["variable"] = "Attended college?"
results_age["variable"] = "Age"
results = [results_under_20, results_gender, results_college, results_age]
results = pd.concat(results)
results = results[['variable','complete', 'missing', 'P-value']]
results_display = pd.DataFrame(results)
display(HTML(results_display.to_html(index=True)))
# -

# # Question 2: Monte Carlo Comparison

# +
# PSet01 functions defined
# -----------------------------------------------------------------------------
methods = ['standard', 'clopper-pearson', 'jeffrey', 'agresti-coull']

def get_ci_binomial(vector, method, level, output_format="pretty"):
    """
    Gives mean estimate and confidence interval using various methods.
    Note that warning messages have been removed.

    Parameters
    ----------
    vector : list or np.array
        An object coercible to an np.array.
    method : str
        One of 'standard', 'clopper-pearson', 'jeffrey', 'agresti-coull'
    level : float between 0 and 1
        The confidence level (e.g. .95)
    output_format : string or None
        If output_format = None, unformatted dictionary is returned.
        Otherwise formatted string is returned.
        
    Returns
    -------
    Point estimate with confidence interval in string or dictionary.
    """
    try:
        np.array(vector)
    except:
        print("Input must be coercible to numpy array type")
    vector = np.array(vector)    
    n = len(vector)
    x = sum(vector)
    p = x/n
    alpha = 1 - level
    z = norm.ppf(level + .5*alpha)
    if method not in methods:
        print(f"Method must be one of {methods}")
    elif method == "standard":
        # if p*n <= 12 or (1-p)*n <=12:
            # print("You may not have sample size / balanced proportions.")
        se = (p*(1-p)/n)**(1/2)
        lwr, upr = p - z*se, p + z*se    
    elif method == "clopper-pearson":
        lwr = beta.ppf(alpha/2, x, n-x+1)
        upr = beta.ppf(1 - alpha/2, x+1, n-x)
    elif method == "jeffrey":
        lwr = max(0, beta.ppf(alpha/2, x+.5, n-x+.5))
        upr = min(1, beta.ppf(1 - alpha/2, x+.5, n-x+.5))
    elif method == "agresti-coull":
        n_tilde = n + z**2
        p_tilde = (x + ((z**2)/2))/n_tilde
        se_tilde = (p_tilde*(1-p_tilde)/n_tilde)**(1/2)
        lwr, upr = p_tilde - z*se_tilde, p_tilde + z*se_tilde
        p = p_tilde
    values = {"est":p, "lwr":lwr, "upr":upr, "level":level}
    if output_format == None:
        return(values)
    else:
        pr = round(p, 4)
        lwrr = round(lwr, 4)
        uprr = round(upr, 4)
        return(f"{pr} [{round(level*100)}% CI: ({lwrr}, {uprr})]".format()) 
# -----------------------------------------------------------------------------


# +
# -----------------------------------------------------------------------------
# Parts a and b: Calibration study
# Let the confidence level of interest be .9

p_vals = [round(.05*i, 2) for i in range(1, 10)]
n_vals = [10**i for i in range(2, 5)]

n_sims = 10000

combs = list(product(p_vals, n_vals))
combs = pd.DataFrame(combs, columns = ["p", "n"])

widths = list(product(p_vals, n_vals))
widths = pd.DataFrame(widths, columns = ["p", "n"])

rng = np.random.default_rng(100)

standard = []
cp = []
jeffrey = []
ac = []

sw = []
cpw = []
jw = []
acw = []

for i in range(len(combs.index)):
    p = combs.iloc[i, ].loc["p"].copy()
    n = combs.iloc[i, ].loc["n"].copy()
    s = rng.binomial(n, p, n_sims)
    contained = []
    avg_width = []
    for value in s:
        binomial_list = [1]*value + [0]*round(n - value)
        binomial_array = np.array(binomial_list)
        intervals = []
        this_width = []
        for method in methods:
            ci = get_ci_binomial(binomial_array, 
                                    method=method, 
                                    level=.9, 
                                    output_format=None)
            intervals.append(ci["lwr"] <= p <= ci["upr"])
            this_width.append(ci["upr"] - ci["lwr"])
        contained.append(intervals)
        avg_width.append(this_width)
    means = pd.DataFrame(contained, columns = methods).mean()
    standard.append(means["standard"])
    cp.append(means["clopper-pearson"])
    jeffrey.append(means['jeffrey'])
    ac.append(means['agresti-coull'])
    ci_widths = pd.DataFrame(avg_width, columns = methods).mean()
    sw.append(ci_widths["standard"])
    cpw.append(ci_widths["clopper-pearson"])
    jw.append(ci_widths['jeffrey'])
    acw.append(ci_widths['agresti-coull'])

combs["standard"] = standard
combs["clopper-pearson"] = cp
combs["jeffrey"] = jeffrey
combs["agresti-coull"] = ac

widths["standard"] = sw
widths["clopper-pearson"] = cpw
widths["jeffrey"] = jw
widths["agresti-coull"] = acw

# combs.to_csv("combs.csv")
# widths.to_csv("widths.csv")
# -



# +
# -----------------------------------------------------------------------------
# part a: Actual coverage countour plot
# Note: have to troubleshoot my matplotlib installation

x = combs["n"]
y = combs["p"]
X, Y = np.meshgrid(x, y)
Z = combs["standard"]

fig, ax = plt.subplots()
CS = ax.contour(X, Y, Z, 20, cmap='RdGy')
ax.clabel(CS, inline=True, fontsize=10)
ax.set_title('Standard CI coverage rate')

# +
# -----------------------------------------------------------------------------
# part b: Width countour plot
# Note: have to troubleshoot my matplotlib installation

x = withds["n"]
y = widths["p"]
X, Y = np.meshgrid(x, y)
Z = widths["standard"]

fig, ax = plt.subplots()
CS = ax.contour(X, Y, Z, 20, cmap='RdGy')
ax.clabel(CS, inline=True, fontsize=10)
ax.set_title('Standard CI width')
# -

# # Appendix: Modified Q3 from PSet 02

# +
# -----------------------------------------------------------------------------
# Part a:

# Set which vars and cohorts to extract
relevant_vars = ["SEQN","RIAGENDR", "RIDAGEYR", "RIDRETH3", "DMDEDUC2", 
                 "DMDMARTL", "RIDSTATR", "SDMVPSU", "SDMVSTRA", 
                 "WTMEC2YR", "WTINT2YR"]
cohort_keys = ["2011-2012/DEMO_G", "2013-2014/DEMO_H", 
               "2015-2016/DEMO_I", "2017-2018/DEMO_J"]

# Gather data from internet
url_part_a = "https://wwwn.cdc.gov/Nchs/Nhanes/"
url_part_c = ".XPT"
all_data = pd.DataFrame(columns=relevant_vars + ["cohort"])
for years in cohort_keys:
    url = url_part_a + years + url_part_c
    df = pd.read_sas(url)
    df = df.loc[:, relevant_vars]
    df["cohort"] = str(years)
    all_data = pd.concat([all_data, df])
    
# Change names and types
new_names = {"SEQN":"respondent_id",
             "RIAGENDR":"gender",
            "RIDAGEYR":"age",
            "RIDRETH3":"race",
            "DMDEDUC2":"educ_level",
            "DMDMARTL":"marital_status",
            "RIDSTATR":"status",
            "SDMVPSU":"psu",
            "SDMVSTRA":"stratum",
            "WTMEC2YR":"weight_exam",
            "WTINT2YR":"weight_interview"}
new_types = {"respondent_id":str,
            "age":int,
            "weight_exam":float,
            "weight_interview":float}
all_data.rename(columns=new_names, inplace=True)
all_data = all_data.astype(dtype=new_types)

# Replace categorical data
gender_dictionary = {1:"Male",
                    2:"Female"}
all_data['gender'] = pd.Categorical(all_data['gender'].replace(gender_dictionary))
race_dictionary = {1: 'Mexican American', 
                   2: 'Other Hispanic',
                   3: 'Non-Hispanic White',
                   4: 'Non-Hispanic Black',
                   6: 'Non-Hispanic Asian',
                   7: 'Other Race / Multiracial'}
all_data['race'] = pd.Categorical(all_data['race'].replace(race_dictionary))
educ_dictionary = {1: 'Less than 9th grade',
                  2: '9-11th grade',
                  3: 'High school graduate / GED',
                  4: 'Some college or AA degree',
                  5: 'College graduate or above',
                  7: 'Refused',
                  9: 'Don\'t know'}
all_data['educ_level'] = pd.Categorical(
    all_data['educ_level'].replace(educ_dictionary))
marital_dictionary = {1: 'Married',
                     2: 'Widowed',
                     3: 'Divorced',
                     4: 'Separated',
                     5: 'Never married',
                     6: 'Living with partner',
                     77: 'Refused',
                     99: 'Don\'t Know'}
all_data['marital_status'] = pd.Categorical(
    all_data['marital_status'].replace(marital_dictionary))
status_dictionary = {1: 'Interviewed only',
                    2: 'Interviewed and examined'}
all_data['status'] = pd.Categorical(
    all_data['status'].replace(status_dictionary))

# Write to pickle
all_data.to_pickle("nhanes_demographic.pkl")
