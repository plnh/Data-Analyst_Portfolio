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

/* Find NUMBER of passanger have travel insurance */
SELECT Have_Insurance, COUNT(*) as passangers
FROM (
	SELECT TravelInsurance,
		CASE WHEN TravelInsurance = 1 THEN 'Yes'
		ELSE 'No'
	END AS Have_Insurance 
	FROM TravelInsurancePrediction ) Insurance
GROUP BY Have_Insurance;

/*Percentage of passsanger have insurance*/
SELECT SUM(CAST(TravelInsurance AS FLOAT))/COUNT(*)*100 AS Percentage_with_Insurance
FROM TravelInsurancePrediction;


SELECT Have_Insurance, Age, COUNT(*) as passangers
FROM (
	SELECT TravelInsurance, Age,
		CASE WHEN TravelInsurance = 1 THEN 'Yes'
		ELSE 'No'
	END AS Have_Insurance 
	FROM TravelInsurancePrediction ) Insurance
GROUP BY Age, Have_Insurance
Order By Age, Have_Insurance;


