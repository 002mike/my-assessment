"""
The database loan.db consists of 5 tables:
   1. customers - table containing customer data
   2. loans - table containing loan data pertaining to customers
   3. credit - table containing credit and creditscore data pertaining to customers
   4. repayments - table containing loan repayment data pertaining to customers
   5. months - table containing month name and month ID data

You are required to make use of your knowledge in SQL to query the database object (saved as loan.db) and return the requested information.
Simply fill in the vacant space wrapped in triple quotes per question (each function represents a question)

NOTE:
The database will be reset when grading each section. Any changes made to the database in the previous `SQL` section can be ignored.
Each question in this section is isolated unless it is stated that questions are linked.
Remember to clean your data

"""


def question_1():
    """
    Make use of a JOIN to find the `AverageIncome` per `CustomerClass`
    """

    # cr - credit database
    # cu - customer database
    qry = """
    SELECT 
        AVG(cu.Income) AS AverageIncome, cr.CustomerClass
    FROM 
        customers cu
    JOIN 
        credit cr
    ON 
        cu.CustomerID = cr.CustomerID
    GROUP BY 
        cr.CustomerClass
    ORDER BY 
        AverageIncome DESC
    """

    return qry


def question_2():
    """
    Make use of a JOIN to return a breakdown of the number of 'RejectedApplications' per 'Province'.
    Ensure consistent use of either the abbreviated or full version of each province, matching the format found in the customer table.
    """

    # lo - loans database
    # cu - customer database
    qry = """
    SELECT 
        COUNT(lo.ApprovalStatus) AS RejectedApplications, 
        (CASE WHEN LCASE(cu.Region) = 'easterncape' THEN 'EC' 
              WHEN LCASE(cu.Region) = 'freestate' THEN 'FS'
              WHEN LCASE(cu.Region) = 'gauteng' THEN 'GT'
              WHEN LCASE(cu.Region) = 'kwazulu-natal' THEN 'KZN'
              WHEN LCASE(cu.Region) = 'limpopo' THEN 'LP' 
              WHEN LCASE(cu.Region) = 'mpumalanga' THEN 'MP'
              WHEN LCASE(cu.Region) = 'northerncape' THEN 'NC'
              WHEN LCASE(cu.Region) = 'northwest' THEN 'NW'
              WHEN LCASE(cu.Region) = 'westerncape' THEN 'WC'
              ELSE cu.Region END) AS Province
    FROM 
        customers cu
    JOIN 
        loans lo
    ON 
        cu.CustomerID = lo.CustomerID
    GROUP BY 
        Province, lo.ApprovalStatus
    HAVING 
        LCASE(lo.ApprovalStatus) = 'rejected'
    ORDER BY 
        RejectedApplications DESC
    """

    return qry


def question_3():
    """
    Making use of the `INSERT` function, create a new table called `financing` which will include the following columns:
    `CustomerID`,`Income`,`LoanAmount`,`LoanTerm`,`InterestRate`,`ApprovalStatus` and `CreditScore`

    Do not return the new table, just create it.
    """

    # lo - loans database
    # cr - credit database
    # cu - customer database
    qry = """
    CREATE TABLE financing (
        CustomerID INT NOT NULL,
        Income INT,
        LoanAmount INT,
        LoanTerm INT,
        InterestRate DECIMAL(5, 2),
        ApprovalStatus VARCHAR(8),
        CreditScore INT
    );

    INSERT INTO financing (CustomerID, Income, LoanAmount, LoanTerm, InterestRate, ApprovalStatus, CreditScore)
    SELECT 
        cu.CustomerID, 
        cu.Income, 
        lo.LoanAmount, 
        lo.LoanTerm, 
        lo.InterestRate, 
        lo.ApprovalStatus, 
        cr.CreditScore
    FROM 
        customers cu
    JOIN 
        credit cr
    ON 
        cu.CustomerID = cr.CustomerID
    JOIN 
        loans lo
    ON 
        cu.CustomerID = lo.CustomerID
    """

    return qry


# Question 4 and 5 are linked


def question_4():
    """
    Using a `CROSS JOIN` and the `months` table, create a new table called `timeline` that sumarises Repayments per customer per month.
    Columns should be: `CustomerID`, `MonthName`, `NumberOfRepayments`, `AmountTotal`.
    Repayments should only occur between 6am and 6pm London Time.
    Null values to be filled with 0.

    Hint: there should be 12x CustomerID = 1.
    """

    # mo - months database
    # cu - customer database
    # re - repayments (suqueried) database
    qry = """
    -- Create timeline table
    
    CREATE TABLE timeline (
        CustomerID INT NOT NULL,
        MonthName VARCHAR(20) NOT NULL,
        NumberOfRepayments INT DEFAULT 0,
        AmountTotal DECIMAL(10, 2) DEFAULT 0.00
    );

    -- Insert values from db's into timeline table
    
    INSERT INTO timeline (CustomerID, MonthName, NumberOfRepayments, AmountTotal)
    SELECT 
        cu.CustomerID, 
        mo.MonthName,
        COALESCE(COUNT(re.RepaymentID), 0) AS NumberOfRepayments,
        COALESCE(SUM(re.Amount), 0.00) AS AmountTotal
    FROM 
        customers cu
    CROSS JOIN 
        months mo
    LEFT JOIN 
        (
            SELECT 
                RepaymentID, 
                CustomerID, 
                Amount, 
                CASE 
                    WHEN TimeZone = 'PST' THEN RepaymentDate - INTERVAL '8 hours'             -- Pacific Standard Time
                    WHEN TimeZone = 'PNT' THEN RepaymentDate - INTERVAL '7 hours'             -- Phoenix Time
                    WHEN TimeZone = 'CST' THEN RepaymentDate - INTERVAL '6 hours'             -- Central Standard Time
                    WHEN TimeZone = 'CET' THEN RepaymentDate + INTERVAL '1 hour'              -- Central European Time
                    WHEN TimeZone = 'EET' THEN RepaymentDate + INTERVAL '2 hours'             -- Eastern European Time
                    WHEN TimeZone = 'IST' THEN RepaymentDate + INTERVAL '5 hours 30 minutes'  -- Indian Standard Time
                    WHEN TimeZone = 'JST' THEN RepaymentDate + INTERVAL '9 hours'             -- Japan Standard Time
                    ELSE RepaymentDate                                                        -- Default (UCT and GMT): no adjustment
                END AS LondonTime
            FROM 
                repayments
        ) re
    ON 
        cu.CustomerID = re.CustomerID 
        AND EXTRACT(HOUR FROM re.LondonTime) BETWEEN 6 AND 18 
        AND strftime('%m', re.LondonTime) = (
            CASE mo.MonthName
                WHEN 'January' THEN '01'
                WHEN 'February' THEN '02'
                WHEN 'March' THEN '03'
                WHEN 'April' THEN '04'
                WHEN 'May' THEN '05'
                WHEN 'June' THEN '06'
                WHEN 'July' THEN '07'
                WHEN 'August' THEN '08'
                WHEN 'September' THEN '09'
                WHEN 'October' THEN '10'
                WHEN 'November' THEN '11'
                WHEN 'December' THEN '12'
            END
        )
    GROUP BY 
        cu.CustomerID, mo.MonthName
    ORDER BY 
        cu.CustomerID;
    """

    return qry


def question_5():
    """
    Make use of conditional aggregation to pivot the `timeline` table such that the columns are as follows:
    `CustomerID`, `JanuaryRepayments`, `JanuaryTotal`,...,`DecemberRepayments`, `DecemberTotal`,...etc
    MonthRepayments columns (e.g JanuaryRepayments) should be integers

    Hint: there should be 1x CustomerID = 1
    """

    qry = """
    SELECT 
        CustomerID,
        -- January
        CAST(SUM(CASE WHEN MonthName = 'January' THEN NumberOfRepayments ELSE 0 END) AS INT) AS JanuaryRepayments,
        SUM(CASE WHEN MonthName = 'January' THEN AmountTotal ELSE 0.00 END) AS JanuaryTotal,
        
        -- February
        CAST(SUM(CASE WHEN MonthName = 'February' THEN NumberOfRepayments ELSE 0 END) AS INT) AS FebruaryRepayments,
        SUM(CASE WHEN MonthName = 'February' THEN AmountTotal ELSE 0.00 END) AS FebruaryTotal,
        
        -- March
        CAST(SUM(CASE WHEN MonthName = 'March' THEN NumberOfRepayments ELSE 0 END) AS INT) AS MarchRepayments,
        SUM(CASE WHEN MonthName = 'March' THEN AmountTotal ELSE 0.00 END) AS MarchTotal,
        
        -- April
        CAST(SUM(CASE WHEN MonthName = 'April' THEN NumberOfRepayments ELSE 0 END) AS INT) AS AprilRepayments,
        SUM(CASE WHEN MonthName = 'April' THEN AmountTotal ELSE 0.00 END) AS AprilTotal,
        
        -- May
        CAST(SUM(CASE WHEN MonthName = 'May' THEN NumberOfRepayments ELSE 0 END) AS INT) AS MayRepayments,
        SUM(CASE WHEN MonthName = 'May' THEN AmountTotal ELSE 0.00 END) AS MayTotal,
        
        -- June
        CAST(SUM(CASE WHEN MonthName = 'June' THEN NumberOfRepayments ELSE 0 END) AS INT) AS JuneRepayments,
        SUM(CASE WHEN MonthName = 'June' THEN AmountTotal ELSE 0.00 END) AS JuneTotal,
        
        -- July
        CAST(SUM(CASE WHEN MonthName = 'July' THEN NumberOfRepayments ELSE 0 END) AS INT) AS JulyRepayments,
        SUM(CASE WHEN MonthName = 'July' THEN AmountTotal ELSE 0.00 END) AS JulyTotal,
        
        -- August
        CAST(SUM(CASE WHEN MonthName = 'August' THEN NumberOfRepayments ELSE 0 END) AS INT) AS AugustRepayments,
        SUM(CASE WHEN MonthName = 'August' THEN AmountTotal ELSE 0.00 END) AS AugustTotal,
        
        -- September
        CAST(SUM(CASE WHEN MonthName = 'September' THEN NumberOfRepayments ELSE 0 END) AS INT) AS SeptemberRepayments,
        SUM(CASE WHEN MonthName = 'September' THEN AmountTotal ELSE 0.00 END) AS SeptemberTotal,
        
        -- October
        CAST(SUM(CASE WHEN MonthName = 'October' THEN NumberOfRepayments ELSE 0 END) AS INT) AS OctoberRepayments,
        SUM(CASE WHEN MonthName = 'October' THEN AmountTotal ELSE 0.00 END) AS OctoberTotal,
        
        -- November
        CAST(SUM(CASE WHEN MonthName = 'November' THEN NumberOfRepayments ELSE 0 END) AS INT) AS NovemberRepayments,
        SUM(CASE WHEN MonthName = 'November' THEN AmountTotal ELSE 0.00 END) AS NovemberTotal,
        
        -- December
        CAST(SUM(CASE WHEN MonthName = 'December' THEN NumberOfRepayments ELSE 0 END) AS INT) AS DecemberRepayments,
        SUM(CASE WHEN MonthName = 'December' THEN AmountTotal ELSE 0.00 END) AS DecemberTotal
    FROM 
        timeline
    GROUP BY 
        CustomerID
    ORDER BY 
        CustomerID;
    """

    return qry


# QUESTION 6 and 7 are linked, Do not be concerned with timezones or repayment times for these question.


def question_6():
    """
    The `customers` table was created by merging two separate tables: one containing data for male customers and the other for female customers.
    Due to an error, the data in the age columns were misaligned in both original tables, resulting in a shift of two places upwards in
    relation to the corresponding CustomerID.

    Create a table called `corrected_customers` with columns: `CustomerID`, `Age`, `CorrectedAge`, `Gender`
    Utilize a window function to correct this mistake in the new `CorrectedAge` column.
    Null values can be input manually - i.e. values that overflow should loop to the top of each gender.

    Also return a result set for this table (ie SELECT * FROM corrected_customers)
    """

    qry = """   
    -- Create the corrected_customers table with corrected data
    CREATE TABLE corrected_customers AS
    SELECT 
        cc.CustomerID,
        cc.Age,
        COALESCE(
            LEAD(cc.Age, 2) OVER (PARTITION BY cc.Gender ORDER BY cc.CustomerID),
            LEAD(cc.Age, 2 - g.TotalRows) OVER (PARTITION BY cc.Gender ORDER BY cc.CustomerID),
            NULL
        ) AS CorrectedAge,
        cc.Gender
    FROM 
        customers cc
    JOIN (
        SELECT 
            Gender,
            COUNT(*) AS TotalRows
        FROM customers
        GROUP BY Gender
    ) g
    ON 
        cc.Gender = g.Gender;
    
    -- Return the result set
    SELECT * FROM corrected_customers;
    """

    return qry


def question_7():
    """
    Create a column in corrected_customers called 'AgeCategory' that categorizes customers by age.
    Age categories should be as follows:
        - `Teen`: CorrectedAge < 20
        - `Young Adult`: 20 <= CorrectedAge < 30
        - `Adult`: 30 <= CorrectedAge < 60
        - `Pensioner`: CorrectedAge >= 60

    Make use of a windows function to assign a rank to each customer based on the total number of repayments per age group. Add this into a "Rank" column.
    The ranking should not skip numbers in the sequence, even when there are ties, i.e. 1,2,2,2,3,4 not 1,2,2,2,5,6
    Customers with no repayments should be included as 0 in the result.

    Return columns: `CustomerID`, `Age`, `CorrectedAge`, `Gender`, `AgeCategory`, `Rank`
    """

    # cc - corrected_customers database
    # re - repayments (suqueried) database
    qry = """
    SELECT *
    FROM (
        SELECT 
            cc.CustomerID,
            cc.Age,
            cc.CorrectedAge,
            cc.Gender,
            CASE
                WHEN cc.CorrectedAge < 20 THEN 'Teen'
                WHEN cc.CorrectedAge >= 20 AND cc.CorrectedAge < 30 THEN 'Young Adult'
                WHEN cc.CorrectedAge >= 30 AND cc.CorrectedAge < 60 THEN 'Adult'
                WHEN cc.CorrectedAge >= 60 THEN 'Pensioner'
                ELSE NULL
            END AS AgeCategory,
            DENSE_RANK() OVER (
                PARTITION BY 
                    CASE
                        WHEN cc.CorrectedAge < 20 THEN 'Teen'
                        WHEN cc.CorrectedAge >= 20 AND cc.CorrectedAge < 30 THEN 'Young Adult'
                        WHEN cc.CorrectedAge >= 30 AND cc.CorrectedAge < 60 THEN 'Adult'
                        WHEN cc.CorrectedAge >= 60 THEN 'Pensioner'
                        ELSE NULL
                    END
                ORDER BY COALESCE(re.TotalRepayments, 0) DESC
            ) AS Rank
        FROM corrected_customers cc
        LEFT JOIN (
            -- Aggregate total repayments per customer
            SELECT 
                CustomerID,
                COUNT(*) AS TotalRepayments
            FROM repayments
            GROUP BY CustomerID
        ) re
        ON cc.CustomerID = re.CustomerID
    ) ranked_data
    -- ORDER BY Rank;

    """

    return qry
