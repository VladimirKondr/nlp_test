#!/usr/bin/env python
# coding: utf-8

# In[ ]:




# In[ ]:


import pandas as pd
from tqdm import tqdm
from include.FurnitureProductExtractor import FurnitureProductExtractor


# In[ ]:


extractor = FurnitureProductExtractor()


# In[ ]:


data = list(set(pd.read_csv('URL_list.csv')["max(page)"].tolist()))
print("Number of urls: ", len(data))
print(data)

data_list = []
for url in tqdm(data):
    products = extractor.process_url(url, True)
    if products and products[0].get("bad request"):
        continue
    names = [product.get('name', '') for product in products]
    data_list.append({"URL": url, "Names": ', '.join(names)})
df = pd.DataFrame(data_list)
df.to_csv('clean_output.csv', index=False)

