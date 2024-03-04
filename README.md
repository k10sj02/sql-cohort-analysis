### Meta Description
This repository contains a comprehensive SQL script for analyzing data from an online commerce platform. The script encompasses various stages of data processing, including database creation, data cleaning, cohort analysis, and reporting. Techniques such as Common Table Expressions (CTEs), Temporary Tables, Window Functions, and the PIVOT function are employed to handle data transformation, calculation, and presentation. The script offers insights into customer behavior, including cohort retention analysis and percentage breakdowns over time. Ideal for understanding online commerce trends and optimizing business strategies.

# SQL Online Commerce Cohort Analysis

# Demystifying the Cohort Table: A Guide to Unlocking Customer Insights

![Dashboard 1 (1)](https://github.com/k10sj02/sql-cohort-analysis/assets/35823259/cac0136b-295b-4437-86d0-27b70e048df2)

**Understanding the Cohort Table: A Step-by-Step Guide**

Cohort tables offer valuable insights into customer behavior by grouping them based on shared attributes, in this case, acquisition date or date of first purchase. Learning to read these tables can be tricky at first but effectively empowers you to analyze customer engagement, retention, and acquisition trends.

**Three Effective Reading Methods:**

1. **Scan Horizontally (Rows):** Allows us to analyze a single cohort's retention rates over time. 
- **Insight:**: The first cohort's retention rate declines from 37% to 27% across twelve months. 
This cohort started with 885 customers (100% retention), and 324 made additional purchases (37%) the following month. This pattern continues, with 286 (32%) making purchases two months later, and so on. We also see that the oldest customers (cohort 1) had the best retention rates despite a steady decline.

2. **Scan Vertically (Columns):** Allows us to compare retention rates for various cohorts within a specific period. Visually scan, looking for columns with similar shades that decrease in intensity (lighter) in subsequent months. This signifies declining retention rates. 
- **Insight:**: For example, in this case, we see that the first two months after the initial purchase shows the most dramatic drop in retention so maybe developing a loyalty campaign around these months may address and halt this trend. In addition, we see that the e-commerce platform acquired far less first-time customers in Dec '11 than it did in Dec '10. Maybe we have exhausted our total addressable market (TAM) or maybe our acquisition strategies are no longer effective. This begs further investigation. 

3. **Scan Diagonally:** Analyze specific month retention rates across all cohorts (e.g., comparing November or Cohort Index 12 retention rates across all cohorts). 
- **Insight:**: Sales in November rise relative to the previous period, revealing a November sales surge observed across all cohorts. This could be due to seasonal factors (perhaps, Thanksgiving or holiday shopping) or a successful marketing campaigns. As an analyst, these insights may fuel further investigation and optimization.

_**Note**: In cohort analysis, you can ignore the last cell since it's the current month i.e. a partial time period. Since the current month is ongoing, data may not be complete or representative of that period._

Cohort analyses become even more powerful when drill down further into a specific attribute. For example, what if we identified that a targeted campaign promoting abandoned carts drove the increase in November sales? We could run another cohort analysis for returning customers that received mobile push notifications or emails. This can help us determine which strategy was more effective.

**Combining Insights and Identifying Opportunities:**

* **Deeper Analysis:** Combining cohort data with domain knowledge provides valuable insights. For example, we can integrate our cohort numbers with purchase data to forecast sales.

**Understanding Limitations:**

* **Data Availability:** Insights might take time to emerge, as data collection can span months or even years.
* **Generalizability:** Cohort analysis focuses on specific groups with shared characteristics, and the derived insights may not be universally applicable to broader contexts.

By mastering cohort table interpretation, you gain a powerful tool to decipher customer behavior and make informed business decisions, ultimately leading to improved customer engagement and retention.
