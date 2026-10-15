-- schema.sql
CREATE DATABASE IF NOT EXISTS sales_analytics;
USE sales_analytics;

CREATE TABLE IF NOT EXISTS sales (
    OrderID INT PRIMARY KEY,
    OrderDate DATETIME,
    Product VARCHAR(255),
    Region VARCHAR(100),
    Quantity INT,
    UnitPrice DECIMAL(10, 2),
    Discount DECIMAL(4, 2),
    CustomerID INT,
    Revenue DECIMAL(12, 2),
    Year INT,
    Month INT,
    DayOfWeek INT,
    IsWeekend TINYINT(1)
);

-- Create indexes for performance
CREATE INDEX idx_order_date ON sales(OrderDate);
CREATE INDEX idx_region ON sales(Region);
CREATE INDEX idx_product ON sales(Product);
