# Stats507
This is my repo with selected solutions I wrote for the Fall 2021 Stats 507 class at UM, compiled for Problem Set 6.

## NHANES Data

The [PSet02 Excerpt](johnston_pset02_excerpt.ipynb) file contains the code needed to download National Health and Nutrition Examination Survey ([NHANES](https://www.cdc.gov/nchs/nhanes/index.htm)) data from 2011-2018.

The script downloads the demographic information data, selects the columns of interest (see below), and recodes categorical variables to have descriptive levels. It does the same for the dentition exam data, and writes both datasets to pickle files.
