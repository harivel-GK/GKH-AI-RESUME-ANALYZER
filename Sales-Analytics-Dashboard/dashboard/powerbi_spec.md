# Power BI Dashboard Specification

## Overview
This document specifies the design and requirements for the Sales Analytics Power BI Dashboard.

## 1. Dashboard Layout
- **Header**: Title ("Global Sales Executive Dashboard"), Company Logo, Last Refreshed Date.
- **Top Row (KPIs)**: 4 Card visuals for immediate metric visibility.
- **Middle Row**: Line chart for Trend Analysis (width: 60%), Donut chart for categorical breakdown (width: 40%).
- **Bottom Row**: Matrix/Table for detailed Product performance, Bar chart for Regional comparison.
- **Left Sidebar**: Slicers for filtering.

## 2. KPI Cards
- Total Revenue (DAX: SUM(Sales[Revenue]))
- Total Orders (DAX: DISTINCTCOUNT(Sales[OrderID]))
- Average Order Value (DAX: AVERAGE(Sales[Revenue]))
- Average Discount % (DAX: AVERAGE(Sales[Discount]))

## 3. Required Visuals
- **Line Chart**: Monthly Revenue Trend (X: Year-Month, Y: Total Revenue)
- **Donut Chart**: Revenue by Region
- **Clustered Bar Chart**: Top 5 Products by Revenue
- **Decomposition Tree**: Break down Revenue -> Region -> Product
- **Matrix**: Product Name, Quantity Sold, Total Revenue, YoY Growth.

## 4. DAX Measures
`dax
Total Revenue = SUM(Sales[Revenue])
Previous Month Revenue = CALCULATE([Total Revenue], PREVIOUSMONTH(Calendar[Date]))
MoM Growth % = DIVIDE([Total Revenue] - [Previous Month Revenue], [Previous Month Revenue], 0)
YTD Revenue = TOTALYTD([Total Revenue], Calendar[Date])
`

## 5. Filters and Slicers
- **Date Slicer**: Relative time (Last 1 Year, This Year, etc.)
- **Region Slicer**: Checkboxes for North, South, East, West
- **Product Category Slicer**: Dropdown

## 6. Theme Recommendations
- **Background**: Dark Gray / Navy Blue (Hex: #1E1E24)
- **Data Colors**: Teal (#008080), Coral (#FF7F50), Gold (#FFD700)
- **Font**: Segoe UI (Standard PBI font), Light for values, Bold for KPIs.
