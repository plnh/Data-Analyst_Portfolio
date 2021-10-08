CREATE TABLE employees (
    employeeID int NOT NULL PRIMARY KEY,
    lastName varchar(255) NOT NULL,
    firstName varchar(255) NOT NULL,
    email varchar(255),
    officeCode varchar(10) NOT NULL,
	managerID int,
	jobTitle varchar(255)) ;

CREATE TABLE offices (
    officeCode varchar(10) NOT NULL PRIMARY KEY,
	city varchar(100) NOT NULL,
	phone int NOT NULL,
	addressLine1 varchar(255),
	addressLine2 varchar(255),
	state varchar(100) NOT NULL,
	country varchar(100) NOT NULL,
	postalCode int )

CREATE TABLE customers (
	customerID int NOT NULL PRIMARY KEY, 
	customerLastName varchar(255) NOT NULL,
	customerFirstName varchar(255) NOT NULL,
	phone int NOT NULL,
	addressLine1 varchar(255),
	addressLine2 varchar(255),
	city varchar(100) NOT NULL,
	state varchar(100) NOT NULL,
	country varchar(100) NOT NULL,
	postalCode int,
	salesRepEmployeeID int NOT NULL,
	creditLimit int)

CREATE TABLE productlines(
	productLine varchar(255) NOT NULL PRIMARY KEY,
	textDescription text)

CREATE TABLE payments (
	customerID int ,
	checkNumber int ,
	paymentDate DATE,
	amount int)

CREATE TABLE orders (
	orderID int NOT NULL PRIMARY KEY,
	orderDate date, 
	requiredDate date,
	shippedDate date,
	status varchar(60),
	comment text,
	customerID int NOT NULL)

CREATE TABLE orderdetails (
	orderID int NOT NULL,
	productCode int NOT NULL,
	quantityOrdered int,
	priceEach float)

CREATE TABLE products (
	productCode int NOT NULL PRIMARY KEY, 
	productName varchar(255),
	productLine varchar(255),
	productVendor varchar(255),
	productDescription text,
	quantityInStock int,
	buyPrice float )

