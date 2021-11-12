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

# # Stat 507, PSet 2 Excerpt for PSet6
# **Heather Johnston**
#
# *Original PSet2 completion: October 1, 2021*
#
# *PSet6 date: November 12, 2021*

# +
import pandas as pd

# The following may be necessary to download sas files from CDC website
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
# -

# ## Problem 3

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

# +
# -----------------------------------------------------------------------------
# Part b

# Define relevant variables
relevant_teeth_vars = ["SEQN", "OHDDESTS"]
tooth_counts = ["OHX" + f"{x:02}" + "TC" 
                for x in range(1, 33)]
cavity_counts = ["OHX" + f"{x:02}" + "CTC" 
                for x in range(2, 32)
                if x != 16 and x != 17]
relevant_teeth_vars = relevant_teeth_vars + tooth_counts + cavity_counts
cohort_keys = ["2011-2012/OHXDEN_G", "2013-2014/OHXDEN_H", 
               "2015-2016/OHXDEN_I", "2017-2018/OHXDEN_J"]

# Download data from internet
url_part_a = "https://wwwn.cdc.gov/Nchs/Nhanes/"
url_part_c = ".XPT"
teeth_data = pd.DataFrame(columns=relevant_teeth_vars + ["cohort"])
for years in cohort_keys:
    url = url_part_a + years + url_part_c
    df = pd.read_sas(url)
    df = df.loc[:, relevant_teeth_vars]
    df["cohort"] = str(years)
    teeth_data = pd.concat([teeth_data, df])
    
teeth_data.head()

# +
new_names = {"SEQN":"respondent_id",
            "OHDDESTS":"dentition_status"}
tooth_count_new_names = ["count_" + f"{x:02}" for x in range(1, 33)]
cavity_new_names = ["cavities_" f"{x:02}"
                for x in range(2, 32)
                if x != 16 and x != 17]
for i, j in zip(tooth_counts + cavity_counts, 
                tooth_count_new_names + cavity_new_names):
    new_names[i] = j

teeth_data.rename(columns=new_names, inplace=True)

dentition_dictionary = {1: 'Complete',
                       2: 'Partial',
                       3: 'Not done'}
teeth_data['dentition_status'] = pd.Categorical(
    teeth_data['dentition_status'].replace(dentition_dictionary))
# -

teeth_data.to_pickle("nhanes_teeth.pkl")

# Part c
print(all_data.shape)
print(teeth_data.shape)
