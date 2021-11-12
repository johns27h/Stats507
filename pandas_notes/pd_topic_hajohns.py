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
# **hajohns@umich.edu**
#
# *Stats 507, Pandas Topics, Fall 2021*

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
