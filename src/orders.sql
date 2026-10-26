select * from orders;

--Question - 1 :
--Find top 10 revenue generated products 

SELECT  PRODUCT_ID ,SALES FROM 
(SELECT PRODUCT_ID , SUM(SALE_PRICE)AS SALES FROM 
ORDERS
GROUP BY PRODUCT_ID 
ORDER BY SALES DESC)
WHERE ROWNUM <=10;

--Question - 2 :
--Find top 5 revenue generated region
WITH CTE AS(
SELECT REGION,PRODUCT_ID,SUM(SALE_PRICE) AS SALES
FROM ORDERS
GROUP BY REGION,PRODUCT_ID
)SELECT * FROM (
SELECT CTE.* , ROW_NUMBER() OVER(PARTITION  BY REGION ORDER BY SALES DESC)AS RN
FROM CTE) A
WHERE RN <=5;

-- Question 3 :
--Find month over month growth comparison for 2022 and 2023 sales eg jan 2022 vs jan 2023

with CTE as (
select 
    extract(year from order_date) as year, 
    extract(month from order_date) as month, 
    sum(sale_price) as sales
    from ORDERS
    GROUP by     extract(year from order_date) , 
    extract(month from order_date) 
    )
    select month,
    sum(case 
    when year = 2022 then sales else 0 end) as year_2022,
    sum (case 
    when year = 2023 then sales else 0 end) as year_2023
    from  cte
    GROUP BY month
    ORDER BY month;

--Question 4 :
--For each category which month had highest sales         
with cte as(
select EXTRACT(year from order_date) as year ,
            extract(month from order_date) as month,
            CATEGORY,
            sum(sale_price) as sales
            from orders
            GROUP by    extract(year from order_date),
                                extract(month from order_date),
                                category
)
select * from 
(
select cte.* ,row_number() over(PARTITION by category order by sales desc)as rn 
 from cte) a
 where rn = 1;
 
-- Question 5 :
--which sub category had highest growth by profit in 2023 compare to 2022
with cte as (
select SUB_CATEGORY,EXTRACT(year from order_date) as year, sum(sale_price) as sales
from orders
GROUP by SUB_CATEGORY,EXTRACT(year from order_date) 
),
cte_2 as(
select 
SUB_CATEGORY,
sum(case 
when year  = 2022 then sales else 0
end) as sales_2022,
sum(case 
when year  = 2023 then sales else 0
end) as sales_2023
from cte
group by SUB_CATEGORY
)
select * from (
select cte_2.*,
ROUND(((sales_2023 - sales_2022) * 100) / sales_2022, 2) AS growth_percentage
from cte_2
order by ROUND(((sales_2023 - sales_2022) * 100) / sales_2022, 2) DESC
)
where ROWNUM = 1
 



