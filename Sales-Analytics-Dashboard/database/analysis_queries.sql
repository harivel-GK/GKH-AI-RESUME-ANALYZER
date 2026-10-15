-- analysis_queries.sql

-- 1. Total Revenue Overview
-- Business Purpose: Calculate the total revenue generated across all time.
SELECT SUM(Revenue) AS TotalRevenue FROM sales;

-- 2. Total Orders Count
-- Business Purpose: Understand order volume.
SELECT COUNT(OrderID) AS TotalOrders FROM sales;

-- 3. Revenue by Region
-- Business Purpose: Identify the best-performing regions.
SELECT Region, SUM(Revenue) AS RegionRevenue FROM sales GROUP BY Region ORDER BY RegionRevenue DESC;

-- 4. Top 5 Best-Selling Products by Revenue
-- Business Purpose: Focus marketing on high-value products.
SELECT Product, SUM(Revenue) AS ProductRevenue FROM sales GROUP BY Product ORDER BY ProductRevenue DESC LIMIT 5;

-- 5. Top 5 Best-Selling Products by Quantity
-- Business Purpose: Understand which items sell the most units.
SELECT Product, SUM(Quantity) AS TotalQuantity FROM sales GROUP BY Product ORDER BY TotalQuantity DESC LIMIT 5;

-- 6. Monthly Revenue Trend
-- Business Purpose: Analyze seasonality and growth over time.
SELECT Year, Month, SUM(Revenue) AS MonthlyRevenue FROM sales GROUP BY Year, Month ORDER BY Year, Month;

-- 7. Average Order Value (AOV)
-- Business Purpose: Key metric for measuring customer purchasing behavior.
SELECT AVG(Revenue) AS AverageOrderValue FROM sales;

-- 8. Customer Purchase Frequency
-- Business Purpose: Identify how often customers are placing orders.
SELECT CustomerID, COUNT(OrderID) AS OrderCount FROM sales GROUP BY CustomerID ORDER BY OrderCount DESC LIMIT 10;

-- 9. Revenue by Day of the Week
-- Business Purpose: Optimize marketing campaigns based on the most active days.
SELECT DayOfWeek, SUM(Revenue) AS DailyRevenue FROM sales GROUP BY DayOfWeek ORDER BY DayOfWeek;

-- 10. Weekend vs Weekday Sales
-- Business Purpose: Understand if weekend promotions are necessary.
SELECT IsWeekend, SUM(Revenue) AS Revenue FROM sales GROUP BY IsWeekend;

-- 11. Discount Impact on Revenue
-- Business Purpose: Analyze if higher discounts lead to higher total revenue.
SELECT Discount, SUM(Revenue) AS TotalRevenue FROM sales GROUP BY Discount ORDER BY Discount;

-- 12. Discount Impact on Quantity Sold
-- Business Purpose: Analyze if higher discounts move more volume.
SELECT Discount, SUM(Quantity) AS TotalQuantity FROM sales GROUP BY Discount ORDER BY Discount;

-- 13. Revenue per Customer (LTV estimation)
-- Business Purpose: Identify highest-value customers.
SELECT CustomerID, SUM(Revenue) AS LifetimeValue FROM sales GROUP BY CustomerID ORDER BY LifetimeValue DESC LIMIT 10;

-- 14. Average Discount given by Region
-- Business Purpose: Identify regional pricing strategies.
SELECT Region, AVG(Discount) AS AvgDiscount FROM sales GROUP BY Region;

-- 15. Lowest Performing Product
-- Business Purpose: Identify products that may need to be discontinued.
SELECT Product, SUM(Revenue) AS Revenue FROM sales GROUP BY Product ORDER BY Revenue ASC LIMIT 1;

-- 16. Monthly Growth Rate (Approximation using LAG)
-- Business Purpose: Track Month-over-Month growth.
WITH MonthlySales AS (
    SELECT Year, Month, SUM(Revenue) AS Rev FROM sales GROUP BY Year, Month
)
SELECT Year, Month, Rev, 
       LAG(Rev) OVER(ORDER BY Year, Month) AS PrevMonthRev,
       ((Rev - LAG(Rev) OVER(ORDER BY Year, Month)) / LAG(Rev) OVER(ORDER BY Year, Month)) * 100 AS GrowthPct
FROM MonthlySales;

-- 17. Orders with High Discounts (>= 15%)
-- Business Purpose: Audit transactions with heavy markdowns.
SELECT OrderID, Product, Discount, Revenue FROM sales WHERE Discount >= 0.15;

-- 18. Average Unit Price by Product
-- Business Purpose: Understand pricing landscape.
SELECT Product, AVG(UnitPrice) AS AvgPrice FROM sales GROUP BY Product;

-- 19. Distinct Customers by Region
-- Business Purpose: Understand customer distribution.
SELECT Region, COUNT(DISTINCT CustomerID) AS UniqueCustomers FROM sales GROUP BY Region;

-- 20. Year-over-Year Revenue
-- Business Purpose: High-level executive summary of annual performance.
SELECT Year, SUM(Revenue) AS AnnualRevenue FROM sales GROUP BY Year ORDER BY Year;
