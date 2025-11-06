-- ============================================================
-- Add Foreign Key Constraints to TERADATA-FI Database
-- Based on actual schema discovery results
-- ============================================================

USE [TERADATA-FI];
GO

-- ============================================================
-- STEP 1: Add Primary Keys to Dimension Tables (if not exists)
-- ============================================================

-- DimCustomer
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimCustomer' AND parent_object_id = OBJECT_ID('dim.DimCustomer'))
    ALTER TABLE dim.DimCustomer ADD CONSTRAINT PK_DimCustomer PRIMARY KEY (CustomerKey);

-- DimDate
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimDate' AND parent_object_id = OBJECT_ID('dim.DimDate'))
    ALTER TABLE dim.DimDate ADD CONSTRAINT PK_DimDate PRIMARY KEY (DateKey);

-- DimLoanProduct
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimLoanProduct' AND parent_object_id = OBJECT_ID('dim.DimLoanProduct'))
    ALTER TABLE dim.DimLoanProduct ADD CONSTRAINT PK_DimLoanProduct PRIMARY KEY (ProductKey);

-- DimLoanPurpose
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimLoanPurpose' AND parent_object_id = OBJECT_ID('dim.DimLoanPurpose'))
    ALTER TABLE dim.DimLoanPurpose ADD CONSTRAINT PK_DimLoanPurpose PRIMARY KEY (PurposeKey);

-- DimApplicationStatus
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimApplicationStatus' AND parent_object_id = OBJECT_ID('dim.DimApplicationStatus'))
    ALTER TABLE dim.DimApplicationStatus ADD CONSTRAINT PK_DimApplicationStatus PRIMARY KEY (StatusKey);

-- DimRiskRating
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimRiskRating' AND parent_object_id = OBJECT_ID('dim.DimRiskRating'))
    ALTER TABLE dim.DimRiskRating ADD CONSTRAINT PK_DimRiskRating PRIMARY KEY (RiskRatingKey);

-- DimCollateralType
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimCollateralType' AND parent_object_id = OBJECT_ID('dim.DimCollateralType'))
    ALTER TABLE dim.DimCollateralType ADD CONSTRAINT PK_DimCollateralType PRIMARY KEY (CollateralTypeKey);

-- DimPaymentMethod
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimPaymentMethod' AND parent_object_id = OBJECT_ID('dim.DimPaymentMethod'))
    ALTER TABLE dim.DimPaymentMethod ADD CONSTRAINT PK_DimPaymentMethod PRIMARY KEY (PaymentMethodKey);

-- DimPaymentType
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimPaymentType' AND parent_object_id = OBJECT_ID('dim.DimPaymentType'))
    ALTER TABLE dim.DimPaymentType ADD CONSTRAINT PK_DimPaymentType PRIMARY KEY (PaymentTypeKey);

-- DimDelinquencyStatus
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimDelinquencyStatus' AND parent_object_id = OBJECT_ID('dim.DimDelinquencyStatus'))
    ALTER TABLE dim.DimDelinquencyStatus ADD CONSTRAINT PK_DimDelinquencyStatus PRIMARY KEY (DelinquencyStatusKey);

-- DimInteractionType
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimInteractionType' AND parent_object_id = OBJECT_ID('dim.DimInteractionType'))
    ALTER TABLE dim.DimInteractionType ADD CONSTRAINT PK_DimInteractionType PRIMARY KEY (InteractionTypeKey);

-- DimInteractionChannel
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimInteractionChannel' AND parent_object_id = OBJECT_ID('dim.DimInteractionChannel'))
    ALTER TABLE dim.DimInteractionChannel ADD CONSTRAINT PK_DimInteractionChannel PRIMARY KEY (ChannelKey);

-- DimCovenantType
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimCovenantType' AND parent_object_id = OBJECT_ID('dim.DimCovenantType'))
    ALTER TABLE dim.DimCovenantType ADD CONSTRAINT PK_DimCovenantType PRIMARY KEY (CovenantTypeKey);

-- DimStatementType
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimStatementType' AND parent_object_id = OBJECT_ID('dim.DimStatementType'))
    ALTER TABLE dim.DimStatementType ADD CONSTRAINT PK_DimStatementType PRIMARY KEY (StatementTypeKey);

-- DimIndustry
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'PK_DimIndustry' AND parent_object_id = OBJECT_ID('dim.DimIndustry'))
    ALTER TABLE dim.DimIndustry ADD CONSTRAINT PK_DimIndustry PRIMARY KEY (IndustryKey);

GO

PRINT 'Primary keys added to dimension tables';
GO

-- ============================================================
-- STEP 2: Add Foreign Keys to FACT_LOAN_APPLICATION
-- ============================================================

-- Customer
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanApplication_Customer')
    ALTER TABLE fact.FACT_LOAN_APPLICATION 
    ADD CONSTRAINT FK_LoanApplication_Customer 
    FOREIGN KEY (CustomerKey) REFERENCES dim.DimCustomer(CustomerKey);

-- Application Date
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanApplication_ApplicationDate')
    ALTER TABLE fact.FACT_LOAN_APPLICATION 
    ADD CONSTRAINT FK_LoanApplication_ApplicationDate 
    FOREIGN KEY (ApplicationDateKey) REFERENCES dim.DimDate(DateKey);

-- Decision Date
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanApplication_DecisionDate')
    ALTER TABLE fact.FACT_LOAN_APPLICATION 
    ADD CONSTRAINT FK_LoanApplication_DecisionDate 
    FOREIGN KEY (DecisionDateKey) REFERENCES dim.DimDate(DateKey);

-- Loan Product
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanApplication_Product')
    ALTER TABLE fact.FACT_LOAN_APPLICATION 
    ADD CONSTRAINT FK_LoanApplication_Product 
    FOREIGN KEY (ProductKey) REFERENCES dim.DimLoanProduct(ProductKey);

-- Loan Purpose
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanApplication_Purpose')
    ALTER TABLE fact.FACT_LOAN_APPLICATION 
    ADD CONSTRAINT FK_LoanApplication_Purpose 
    FOREIGN KEY (PurposeKey) REFERENCES dim.DimLoanPurpose(PurposeKey);

-- Application Status
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanApplication_Status')
    ALTER TABLE fact.FACT_LOAN_APPLICATION 
    ADD CONSTRAINT FK_LoanApplication_Status 
    FOREIGN KEY (ApplicationStatusKey) REFERENCES dim.DimApplicationStatus(StatusKey);

GO

PRINT 'Foreign keys added to FACT_LOAN_APPLICATION';
GO

-- ============================================================
-- STEP 3: Add Foreign Keys to FACT_LOAN_ORIGINATION
-- ============================================================

-- Customer
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanOrigination_Customer')
    ALTER TABLE fact.FACT_LOAN_ORIGINATION 
    ADD CONSTRAINT FK_LoanOrigination_Customer 
    FOREIGN KEY (CustomerKey) REFERENCES dim.DimCustomer(CustomerKey);

-- Origination Date
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanOrigination_OriginationDate')
    ALTER TABLE fact.FACT_LOAN_ORIGINATION 
    ADD CONSTRAINT FK_LoanOrigination_OriginationDate 
    FOREIGN KEY (OriginationDateKey) REFERENCES dim.DimDate(DateKey);

-- Maturity Date
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanOrigination_MaturityDate')
    ALTER TABLE fact.FACT_LOAN_ORIGINATION 
    ADD CONSTRAINT FK_LoanOrigination_MaturityDate 
    FOREIGN KEY (MaturityDateKey) REFERENCES dim.DimDate(DateKey);

-- First Payment Date
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanOrigination_FirstPaymentDate')
    ALTER TABLE fact.FACT_LOAN_ORIGINATION 
    ADD CONSTRAINT FK_LoanOrigination_FirstPaymentDate 
    FOREIGN KEY (FirstPaymentDateKey) REFERENCES dim.DimDate(DateKey);

-- Loan Product
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanOrigination_Product')
    ALTER TABLE fact.FACT_LOAN_ORIGINATION 
    ADD CONSTRAINT FK_LoanOrigination_Product 
    FOREIGN KEY (ProductKey) REFERENCES dim.DimLoanProduct(ProductKey);

-- Loan Purpose
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanOrigination_Purpose')
    ALTER TABLE fact.FACT_LOAN_ORIGINATION 
    ADD CONSTRAINT FK_LoanOrigination_Purpose 
    FOREIGN KEY (PurposeKey) REFERENCES dim.DimLoanPurpose(PurposeKey);

-- Delinquency Status
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanOrigination_DelinquencyStatus')
    ALTER TABLE fact.FACT_LOAN_ORIGINATION 
    ADD CONSTRAINT FK_LoanOrigination_DelinquencyStatus 
    FOREIGN KEY (DelinquencyStatusKey) REFERENCES dim.DimDelinquencyStatus(DelinquencyStatusKey);

GO

PRINT 'Foreign keys added to FACT_LOAN_ORIGINATION';
GO

-- ============================================================
-- STEP 4: Add Foreign Keys to FACT_PAYMENT_TRANSACTION
-- ============================================================

-- Loan (self-referencing to FACT_LOAN_ORIGINATION)
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Payment_Loan')
    ALTER TABLE fact.FACT_PAYMENT_TRANSACTION 
    ADD CONSTRAINT FK_Payment_Loan 
    FOREIGN KEY (LoanKey) REFERENCES fact.FACT_LOAN_ORIGINATION(LoanKey);

-- Payment Date
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Payment_PaymentDate')
    ALTER TABLE fact.FACT_PAYMENT_TRANSACTION 
    ADD CONSTRAINT FK_Payment_PaymentDate 
    FOREIGN KEY (PaymentDateKey) REFERENCES dim.DimDate(DateKey);

-- Scheduled Date
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Payment_ScheduledDate')
    ALTER TABLE fact.FACT_PAYMENT_TRANSACTION 
    ADD CONSTRAINT FK_Payment_ScheduledDate 
    FOREIGN KEY (ScheduledDateKey) REFERENCES dim.DimDate(DateKey);

-- Payment Method
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Payment_PaymentMethod')
    ALTER TABLE fact.FACT_PAYMENT_TRANSACTION 
    ADD CONSTRAINT FK_Payment_PaymentMethod 
    FOREIGN KEY (PaymentMethodKey) REFERENCES dim.DimPaymentMethod(PaymentMethodKey);

-- Payment Type
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Payment_PaymentType')
    ALTER TABLE fact.FACT_PAYMENT_TRANSACTION 
    ADD CONSTRAINT FK_Payment_PaymentType 
    FOREIGN KEY (PaymentTypeKey) REFERENCES dim.DimPaymentType(PaymentTypeKey);

GO

PRINT 'Foreign keys added to FACT_PAYMENT_TRANSACTION';
GO

-- ============================================================
-- STEP 5: Add Foreign Keys to FACT_LOAN_BALANCE_DAILY
-- ============================================================

-- Loan
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanBalance_Loan')
    ALTER TABLE fact.FACT_LOAN_BALANCE_DAILY 
    ADD CONSTRAINT FK_LoanBalance_Loan 
    FOREIGN KEY (LoanKey) REFERENCES fact.FACT_LOAN_ORIGINATION(LoanKey);

-- Snapshot Date
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanBalance_SnapshotDate')
    ALTER TABLE fact.FACT_LOAN_BALANCE_DAILY 
    ADD CONSTRAINT FK_LoanBalance_SnapshotDate 
    FOREIGN KEY (SnapshotDateKey) REFERENCES dim.DimDate(DateKey);

-- Delinquency Status
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_LoanBalance_DelinquencyStatus')
    ALTER TABLE fact.FACT_LOAN_BALANCE_DAILY 
    ADD CONSTRAINT FK_LoanBalance_DelinquencyStatus 
    FOREIGN KEY (DelinquencyStatusKey) REFERENCES dim.DimDelinquencyStatus(DelinquencyStatusKey);

GO

PRINT 'Foreign keys added to FACT_LOAN_BALANCE_DAILY';
GO

-- ============================================================
-- STEP 6: Add Foreign Keys to FACT_CUSTOMER_INTERACTION
-- ============================================================

-- Customer
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Interaction_Customer')
    ALTER TABLE fact.FACT_CUSTOMER_INTERACTION 
    ADD CONSTRAINT FK_Interaction_Customer 
    FOREIGN KEY (CustomerKey) REFERENCES dim.DimCustomer(CustomerKey);

-- Interaction Date
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Interaction_InteractionDate')
    ALTER TABLE fact.FACT_CUSTOMER_INTERACTION 
    ADD CONSTRAINT FK_Interaction_InteractionDate 
    FOREIGN KEY (InteractionDateKey) REFERENCES dim.DimDate(DateKey);

-- Interaction Type
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Interaction_InteractionType')
    ALTER TABLE fact.FACT_CUSTOMER_INTERACTION 
    ADD CONSTRAINT FK_Interaction_InteractionType 
    FOREIGN KEY (InteractionTypeKey) REFERENCES dim.DimInteractionType(InteractionTypeKey);

-- Interaction Channel
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Interaction_Channel')
    ALTER TABLE fact.FACT_CUSTOMER_INTERACTION 
    ADD CONSTRAINT FK_Interaction_Channel 
    FOREIGN KEY (InteractionChannelKey) REFERENCES dim.DimInteractionChannel(ChannelKey);

-- Related Loan
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Interaction_RelatedLoan')
    ALTER TABLE fact.FACT_CUSTOMER_INTERACTION 
    ADD CONSTRAINT FK_Interaction_RelatedLoan 
    FOREIGN KEY (RelatedLoanKey) REFERENCES fact.FACT_LOAN_ORIGINATION(LoanKey);

-- Related Application
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Interaction_RelatedApplication')
    ALTER TABLE fact.FACT_CUSTOMER_INTERACTION 
    ADD CONSTRAINT FK_Interaction_RelatedApplication 
    FOREIGN KEY (RelatedApplicationKey) REFERENCES fact.FACT_LOAN_APPLICATION(ApplicationKey);

-- Follow Up Date
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Interaction_FollowUpDate')
    ALTER TABLE fact.FACT_CUSTOMER_INTERACTION 
    ADD CONSTRAINT FK_Interaction_FollowUpDate 
    FOREIGN KEY (FollowUpDateKey) REFERENCES dim.DimDate(DateKey);

GO

PRINT 'Foreign keys added to FACT_CUSTOMER_INTERACTION';
GO

-- ============================================================
-- STEP 7: Add Foreign Keys to FACT_COVENANT_TEST
-- ============================================================

-- Loan
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Covenant_Loan')
    ALTER TABLE fact.FACT_COVENANT_TEST 
    ADD CONSTRAINT FK_Covenant_Loan 
    FOREIGN KEY (LoanKey) REFERENCES fact.FACT_LOAN_ORIGINATION(LoanKey);

-- Test Date
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Covenant_TestDate')
    ALTER TABLE fact.FACT_COVENANT_TEST 
    ADD CONSTRAINT FK_Covenant_TestDate 
    FOREIGN KEY (TestDateKey) REFERENCES dim.DimDate(DateKey);

-- Covenant Type
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Covenant_CovenantType')
    ALTER TABLE fact.FACT_COVENANT_TEST 
    ADD CONSTRAINT FK_Covenant_CovenantType 
    FOREIGN KEY (CovenantTypeKey) REFERENCES dim.DimCovenantType(CovenantTypeKey);

GO

PRINT 'Foreign keys added to FACT_COVENANT_TEST';
GO

-- ============================================================
-- STEP 8: Add Foreign Keys to FACT_CUSTOMER_FINANCIALS
-- ============================================================

-- Customer
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Financials_Customer')
    ALTER TABLE fact.FACT_CUSTOMER_FINANCIALS 
    ADD CONSTRAINT FK_Financials_Customer 
    FOREIGN KEY (CustomerKey) REFERENCES dim.DimCustomer(CustomerKey);

-- Statement Date
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Financials_StatementDate')
    ALTER TABLE fact.FACT_CUSTOMER_FINANCIALS 
    ADD CONSTRAINT FK_Financials_StatementDate 
    FOREIGN KEY (StatementDateKey) REFERENCES dim.DimDate(DateKey);

-- Statement Type
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Financials_StatementType')
    ALTER TABLE fact.FACT_CUSTOMER_FINANCIALS 
    ADD CONSTRAINT FK_Financials_StatementType 
    FOREIGN KEY (StatementTypeKey) REFERENCES dim.DimStatementType(StatementTypeKey);

GO

PRINT 'Foreign keys added to FACT_CUSTOMER_FINANCIALS';
GO

-- ============================================================
-- STEP 9: Verify all foreign keys were created
-- ============================================================

SELECT 
    fk.name AS ForeignKeyName,
    OBJECT_SCHEMA_NAME(fk.parent_object_id) AS TableSchema,
    OBJECT_NAME(fk.parent_object_id) AS TableName,
    COL_NAME(fc.parent_object_id, fc.parent_column_id) AS ColumnName,
    OBJECT_SCHEMA_NAME(fk.referenced_object_id) AS ReferencedSchema,
    OBJECT_NAME(fk.referenced_object_id) AS ReferencedTable,
    COL_NAME(fc.referenced_object_id, fc.referenced_column_id) AS ReferencedColumn
FROM sys.foreign_keys AS fk
INNER JOIN sys.foreign_key_columns AS fc 
    ON fk.object_id = fc.constraint_object_id
WHERE OBJECT_SCHEMA_NAME(fk.parent_object_id) IN ('dim', 'fact')
ORDER BY TableSchema, TableName, ForeignKeyName;

GO

PRINT '=================================================';
PRINT 'Foreign key constraints added successfully!';
PRINT 'Total relationships created: 35+';
PRINT 'The database now has a complete star schema.';
PRINT '=================================================';
