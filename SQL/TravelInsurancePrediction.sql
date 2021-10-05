/*Read all columns of the 1st 5 rows */
SELECT TOP 5 *
FROM TravelInsurancePrediction; 

/*Delete the empty column*/
ALTER TABLE TravelInsurancePrediction
DROP COLUMN [Column1];

/*Check if there null value */
SELECT * 
FROM TravelInsurancePrediction
WHERE Age IS NULL OR AnnualIncome IS NULL OR TravelInsurance IS NULL ;

/* */
SELECT MIN(Age) as min_age, MAX(Age) as max_age, 
	MIN(AnnualIncome) as min_income, MAX(AnnualIncome) as max_income
FROM TravelInsurancePrediction

/*There is an error in annual income as there's extra 0*/
UPDATE TravelInsurancePrediction 
SET AnnualIncome = AnnualIncome/10

/* Find NUMBER of passanger have travel insurance */
SELECT Have_Insurance, COUNT(*) as passangers,
		COUNT(TravelInsurance) * 100.00 /SUM(COUNT(TravelInsurance)) OVER () AS Percentage_with_Insurance
FROM (
	SELECT TravelInsurance,
		CASE WHEN TravelInsurance = 1 THEN 'Yes'
		ELSE 'No'
	END AS Have_Insurance 
	FROM TravelInsurancePrediction ) Insurance
GROUP BY Have_Insurance;


/*passsanger have insurance per age*/
SELECT Age, SUM(TravelInsurance) as With_Insurance,
		SUM(TravelInsurance) * 100.0 / SUM(SUM(TravelInsurance)) OVER () AS Percentage_With_Ins
FROM TravelInsurancePrediction
GROUP BY Age 
Order By Age;

/*Percentage of passsanger have insurance per each age segment*/
WITH AgeBins AS
(
SELECT 
    CASE 
        WHEN Age >= 25 and Age <= 27 THEN 'Mid 20s'
        WHEN Age >= 28 and Age <= 30 THEN 'Late 20s'
        WHEN Age >= 31 and Age <= 33 THEN 'Early 30s'
        WHEN Age > 33 THEN 'Mid 30s'
    END as age_bins,
    TravelInsurance
FROM TravelInsurancePrediction
)

SELECT
    age_bins,
    SUM(TravelInsurance) AS With_Insurance,
	SUM(TravelInsurance) * 100.0 / SUM(SUM(TravelInsurance)) OVER () AS Percentage_With_Ins,
	SUM(TravelInsurance) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY age_bins) AS Percentage_Total_Bins
FROM AgeBins
GROUP BY age_bins
ORDER BY 
	(CASE age_bins
		WHEN 'Mid 20s' THEN 1
		WHEN 'Late 20s' THEN 2
		WHEN 'Early 30s' THEN 3 
		WHEN 'Mid 30s' THEN 4
		END) ASC;


/*passsanger have insurance per income*/
SELECT AnnualIncome, SUM(TravelInsurance) as With_Insurance,
		SUM(TravelInsurance) * 100.0 / SUM(SUM(TravelInsurance)) OVER () AS Percentage_With_Ins
FROM TravelInsurancePrediction
GROUP BY AnnualIncome 
Order By AnnualIncome;


/*Percentage of passsanger have insurance per each income segment*/
WITH IncomeBins AS
(
SELECT 
    CASE 
        WHEN AnnualIncome <= 40100 THEN 'Low Incomes'
        WHEN AnnualIncome > 40100 and AnnualIncome <= 102400 THEN 'Mid Income'
        WHEN AnnualIncome > 102400 THEN 'High Incomes'
    END as incomes,
    TravelInsurance
FROM TravelInsurancePrediction
)

SELECT
    incomes,
    SUM(TravelInsurance) AS With_Insurance,
	SUM(TravelInsurance) * 100.0 / SUM(SUM(TravelInsurance)) OVER () AS Percentage_With_Ins,
	SUM(TravelInsurance) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY incomes) AS Percentage_Total_Bins
FROM IncomeBins
GROUP BY incomes
ORDER BY 
	(CASE incomes
		WHEN 'Low Incomes' THEN 1
		WHEN 'Mid Income' THEN 2
		WHEN 'High Incomes' THEN 3
		END) ASC;

/* AGE AND INCOME WITH INSURANCE*/
WITH AgeIncome AS
(
SELECT 
    CASE 
        WHEN Age >= 25 and Age <= 27 THEN 'Mid 20s'
        WHEN Age >= 28 and Age <= 30 THEN 'Late 20s'
        WHEN Age >= 31 and Age <= 33 THEN 'Early 30s'
        WHEN Age > 33 THEN 'Mid 30s'
    END as age_bins,
	CASE 
        WHEN AnnualIncome <= 40100 THEN 'Low Incomes'
        WHEN AnnualIncome > 40100 and AnnualIncome <= 102400 THEN 'Mid Income'
        WHEN AnnualIncome > 102400 THEN 'High Incomes'
    END as incomes,
    TravelInsurance
FROM TravelInsurancePrediction
)

SELECT
    incomes, age_bins,
    SUM(TravelInsurance) AS With_Insurance,
	SUM(TravelInsurance) * 100.0 / SUM(SUM(TravelInsurance)) OVER () AS Percentage_With_Ins,
	SUM(TravelInsurance) * 100.0 / SUM(COUNT(TravelInsurance)) OVER () AS Percentage_Total
FROM AgeIncome
GROUP BY age_bins, incomes
ORDER BY 
	(CASE incomes
		WHEN 'Low Incomes' THEN 1
		WHEN 'Mid Income' THEN 2
		WHEN 'High Incomes' THEN 3
		END) ASC,
		(CASE age_bins
		WHEN 'Mid 20s' THEN 1
		WHEN 'Late 20s' THEN 2
		WHEN 'Early 30s' THEN 3 
		WHEN 'Mid 30s' THEN 4
		END) ASC
;

/*passsanger have insurance with Chronic diseases*/
SELECT 
		ChronicDiseases, 
		COUNT(*) AS Passanger,
		COUNT(*) * 100.00 / SUM(COUNT(*)) OVER () AS Percentage_Total,
		SUM(TravelInsurance) as With_Insurance,
		SUM(TravelInsurance) * 100.0 / SUM(SUM(TravelInsurance)) OVER () AS Percentage_With_Ins		
FROM TravelInsurancePrediction
GROUP BY ChronicDiseases 
Order By ChronicDiseases;

/*passsanger have insurance and frequentflyer*/
SELECT 
		FrequentFlyer, 
		COUNT(*) as Passanger,
		COUNT(*) * 100.00 / SUM(COUNT(*)) OVER () AS Percentage_Total,
		SUM(TravelInsurance) as With_Insurance,
		SUM(TravelInsurance) * 100.0 / SUM(SUM(TravelInsurance)) OVER () AS Percentage_With_Ins
FROM TravelInsurancePrediction
GROUP BY FrequentFlyer 
Order By FrequentFlyer;


/*passsanger have insurance and Travel aboard*/
SELECT 
		EverTravelledAbroad, 
		COUNT(*) as Passanger,
		COUNT(*) * 100.00 / SUM(COUNT(*)) OVER () AS Percentage_Total,
		SUM(TravelInsurance) as With_Insurance,
		SUM(TravelInsurance) * 100.0 / SUM(SUM(TravelInsurance)) OVER () AS Percentage_With_Ins
FROM TravelInsurancePrediction
GROUP BY EverTravelledAbroad 
Order By EverTravelledAbroad;
