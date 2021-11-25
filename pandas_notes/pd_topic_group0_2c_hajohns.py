# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_json: true
#     notebook_metadata_filter: markdown
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

# ## Topics in Pandas
# **Stats 507, Fall 2021** 
#
# **Group 0**
#   

import pandas as pd
import numpy as np

# ## Contents
# Add a bullet for each topic and link to the level 2 title header using 
# the exact title with spaces replaced by a dash. 
#
# + [Pivot tables](#Pivot-tables)
# + [One row to many](#One-row-to-many)
# + [DataFrame.pct_change()](#DataFrame.pct_change()) 
# + [Working with missing data](#Working-with-missing-data)
# + [Cumulative sums](#Title:-pandas.DataFrame.cumsum)
# + [Stack and unstack](#Stack-and-unstack)
#

# ## Pivot tables
# Zeyuan Li
# zeyuanli@umich.edu
# 10/19/2021
#
#

# ## Pivot tables in pandas
#
# The pivot tables in Excel is very powerful and convienent in handling with numeric data. Pandas also provides ```pivot_table()``` for pivoting with aggregation of numeric data. There are 5 main arguments of ```pivot_table()```:
# * ***data***: a DataFrame object
# * ***values***: a column or a list of columns to aggregate.
# * ***index***: Keys to group by on the pivot table index. 
# * ***columns***:  Keys to group by on the pivot table column. 
# * ***aggfunc***: function to use for aggregation, defaulting to ```numpy.mean```.

# ### Example

df = pd.DataFrame(
    {
        "A": ["one", "one", "two", "three"] * 6,
        "B": ["A", "B", "C"] * 8,
        "C": ["foo", "foo", "foo", "bar", "bar", "bar"] * 4,
        "D": np.random.randn(24),
        "E": np.random.randn(24),
        "F": [datetime.datetime(2013, i, 1) for i in range(1, 13)]
        + [datetime.datetime(2013, i, 15) for i in range(1, 13)],
    }
)
df


# ### Do aggregation
#
# * Get the pivot table easily. 
# * Produce the table as the same result of doing ```groupby(['A','B','C'])``` and compute the ```mean``` of D, with different values of D shown in seperate columns.
# * Change to another ***aggfunc*** to finish the aggregation as you want.

pd.pivot_table(df, values="D", index=["A", "B"], columns=["C"])


pd.pivot_table(df, values="D", index=["B"], columns=["A", "C"], aggfunc=np.sum)


# ### Display all aggregation values
#
# * If the ***values*** column name is not given, the pivot table will include all of the data that can be aggregated in an additional level of hierarchy in the columns:

pd.pivot_table(df, index=["A", "B"], columns=["C"])


# ### Output
#
# * You can render a nice output of the table omitting the missing values by calling ```to_string```

table = pd.pivot_table(df, index=["A", "B"], columns=["C"])
print(table.to_string(na_rep=""))

# ## One row to many
#
# *Kunheng Li(kunhengl@umich.edu)*

# The reason I choose this function is because last homework. Before the hint from teachers, I found some ways to transfrom one row to many rows. Therefore, I will introduce a function to deal with this type of data.

# First, let's see an example.

data = {
    "first name":["kevin","betty","tony"],
    "last name":["li","jin","zhang"],
    "courses":["EECS484, STATS507","STATS507, STATS500","EECS402,EECS482,EECS491"]   
}
df = pd.DataFrame(data)
df = df.set_index(["first name", "last name"])["courses"].str.split(",", expand=True)\
    .stack().reset_index(drop=True, level=-1).reset_index().rename(columns={0: "courses"})
print(df)

# This is the first method I want to introduce, stack() or unstack(), both are similar. 
# Unstack() and stack() in DataFrame are to make itself to a Series which has secondary index.
# Unstack() is to transform its index to secondary index and its column to primary index, however, 
# stack() is to transform its index to primary index and its column to secondary index.

# However, in Pandas 0.25 version, there is a new method in DataFrame called explode(). They have the result, let's see the example.

df["courses"] = df["courses"].str.split(",")
df = df.explode("courses")
print(df)


# ## DataFrame.pct_change()
# *Dongming Yang*

# +
# This function always be used to calculate the percentage change between the current and a prior element, and always be used to a time series     
# The axis could choose the percentage change from row or columns
# Creating the time-series index 
ind = pd.date_range('01/01/2000', periods = 6, freq ='W') 
  
# Creating the dataframe  
df = pd.DataFrame({"A":[14, 4, 5, 4, 1, 55], 
                   "B":[5, 2, 54, 3, 2, 32],  
                   "C":[20, 20, 7, 21, 8, 5], 
                   "D":[14, 3, 6, 2, 6, 4]}, index = ind) 
  
# find the percentage change with the previous row 
df.pct_change()

# find the percentage change with precvious columns 
df.pct_change(axis=1)m

# +
# periods means start to calculate the percentage change between the periods column or row and the beginning

# find the specific percentage change with first row
df.pct_change(periods=3)

# +
# fill_method means the way to handle NAs before computing percentage change by assigning a value to that NAs
# importing pandas as pd 
import pandas as pd 
  
# Creating the time-series index 
ind = pd.date_range('01/01/2000', periods = 6, freq ='W') 
  
# Creating the dataframe  
df = pd.DataFrame({"A":[14, 4, 5, 4, 1, 55], 
                   "B":[5, 2, None, 3, 2, 32],  
                   "C":[20, 20, 7, 21, 8, None], 
                   "D":[14, None, 6, 2, 6, 4]}, index = ind) 
  
# apply the pct_change() method 
# we use the forward fill method to 
# fill the missing values in the dataframe 
df.pct_change(fill_method ='ffill')

# ## Contents
# Add a bullet for each topic and link to the level 2 title header using 
# the exact title with spaces replaced by a dash. 
#
# -

# ## Working with missing data
# *Kailan Xu*

# - Detecting missing data
# - Inserting missing data
# - Calculations with missing data
# - Cleaning / filling missing data
# - Dropping axis labels with missing data

# ### 1. Detecting missing data

# As data comes in many shapes and forms, pandas aims to be flexible with regard to handling missing data. While NaN is the default missing value marker for reasons of computational speed and convenience, we need to be able to easily detect this value with data of different types: floating point, integer, boolean, and general object. In many cases, however, the Python None will arise and we wish to also consider that “missing” or “not available” or “NA”.

# +
import pandas as pd 
import numpy as np 

df = pd.DataFrame(
    np.random.randn(5, 3),
    index=["a", "c", "e", "f", "h"],
    columns=["one", "two", "three"],
)
df2 = df.reindex(["a", "b", "c", "d", "e", "f", "g", "h"])
df2
# -

# To make detecting missing values easier (and across different array dtypes), pandas provides the `isna()` and `notna()` functions, which are also methods on Series and DataFrame objects:

df2.isna()

df2.notna()

# ###  2. Inserting missing data

# You can insert missing values by simply assigning to containers. The actual missing value used will be chosen based on the dtype.
# For example, numeric containers will always use NaN regardless of the missing value type chosen:

s = pd.Series([1, 2, 3])
s.loc[0] = None
s

# Likewise, datetime containers will always use NaT.
# For object containers, pandas will use the value given:

s = pd.Series(["a", "b", "c"])
s.loc[0] = None
s.loc[1] = np.nan
s

# ### 3. Calculations with missing data

# - When summing data, NA (missing) values will be treated as zero.
# - If the data are all NA, the result will be 0.
# - Cumulative methods like `cumsum()` and `cumprod()` ignore NA values by default, but preserve them in the resulting arrays. To override this behaviour and include NA values, use `skipna=False`.

df2

df2["one"].sum()

df2.mean(1)

df2.cumsum()

df2.cumsum(skipna=False)

# ### 4. Cleaning / filling missing data

# pandas objects are equipped with various data manipulation methods for dealing with missing data.
# - `fillna()` can “fill in” NA values with non-NA data in a couple of ways, which we illustrate:

df2.fillna(0)

df2["one"].fillna("missing")

# ### 5.Dropping axis labels with missing data

# You may wish to simply exclude labels from a data set which refer to missing data. To do this, use `dropna()`:

df2.dropna(axis=0)


# # Title: pandas.DataFrame.cumsum
# - Name: Yixuan Feng
# - Email: fengyx@umich.edu

# ## pandas.DataFrame.cumsum
# - Cumsum is the cumulative function of pandas, used to return the cumulative values of columns or rows.

# ## Example 1 - Without Setting Parameters
# - This function will automatically return the cumulative value of all columns.

values_1 = np.random.randint(10, size=10) 
values_2 = np.random.randint(10, size=10) 
group = ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C', 'A'] 
df = pd.DataFrame({'group':group, 'value_1':values_1, 'value_2':values_2}) 
df

df.cumsum()

# ## Example 2 - Setting Parameters
# - By setting the axis to 1, this function will return the cumulative value of all rows.
# - By combining with groupby() function, other columns (or rows) can be used as references for cumulative addition.

df['cumsum_2'] = df[['group', 'value_2']].groupby('group').cumsum() 
df

# [link](https://github.com/fyx1009/Stats507/blob/main/pandas_notes/pd_topic_fengyx.py)

# ## Stack and Unstack
# **Heather Johnston**
#
# **hajohns@umich.edu**
#
# *Stats 507, Pandas Topics, Fall 2021*
#
# ### About stack and unstack
# * Stack and Unstack are similar to "melt" and "pivot" methods for transforming data
# * R users may be familiar with "pivot_wider" and "pivot_longer" (formerly "spread" and "gather")
# * Stack transforms column names to new index and values to column
#
# ### Example: Stack
# * Consider the `example` DataFrame below to be measurements of some value taken on different days at different times.
# * It would be natural to want these to be "gathered" into long format, which we can do using `stack`

example = pd.DataFrame({"day":["Monday", "Wednesday", "Friday"],
                        "morning":[4, 5, 6],
                        "afternoon":[8, 9, 0]})
example.set_index("day", inplace=True)
print(example)
print(example.stack())

# ### Example: Unstack
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

