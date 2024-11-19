-- CREATE TABLE tblReportEmployeeInfo (Month varchar(3), Year int, Working int, Terminated int, Maternity int, BeforeMaternity int, NewHire int)
if object_id('[dbo].[sptblReportEmployeeInfo]') is null
	EXEC ('CREATE PROCEDURE [dbo].[sptblReportEmployeeInfo] as select 1')
GO
ALTER PROCEDURE [dbo].[sptblReportEmployeeInfo](@Year int = 2022)
AS
	-- Procedure for counting information entered into the table tblReportEmployeeInfo
	DELETE tblReportEmployeeInfo WHERE Year = @Year
	SELECT * INTO #ReportEmployeeInfo FROM tblReportEmployeeInfo WHERE 1 = 0

	DECLARE @RunStep int = 1, @ToDate datetime, @FromDate datetime
	WHILE (@RunStep <= 12)
	BEGIN
		SELECT @FromDate = FromDate,  @ToDate = ToDate FROM dbo.fn_Get_SalaryPeriod(@RunStep, @Year)
		SELECT EmployeeID, HireDate, TerminateDate, EmployeeStatusID
		INTO #fn_vtblEmployeeList_Bydate
		FROM dbo.fn_vtblEmployeeList_Bydate(@ToDate,'-1',NULL) WHERE TerminateDate is null or TerminateDate >= @FromDate

        IF (GETDATE()> @FromDate)
        BEGIN 
		INSERT INTO #ReportEmployeeInfo (Month, Year, Working, Terminated, Maternity, BeforeMaternity, NewHire)
		SELECT convert(varchar(3), @FromDate, 107), @Year,
			   COUNT(1) as Working,
			   (SELECT COUNT(1) FROM #fn_vtblEmployeeList_Bydate WHERE TerminateDate between @FromDate and @ToDate) as Terminated,
			   (SELECT COUNT(1) FROM #fn_vtblEmployeeList_Bydate WHERE EmployeeStatusID = 1) as Maternity,
			   (SELECT COUNT(1) FROM #fn_vtblEmployeeList_Bydate WHERE EmployeeStatusID = 11) as Maternity,
			   (SELECT COUNT(1) FROM #fn_vtblEmployeeList_Bydate WHERE HireDate between @FromDate and @ToDate) as NewHire
		FROM #fn_vtblEmployeeList_Bydate
		WHERE TerminateDate is null
        END
		SET @RunStep = @RunStep + 1
		DROP TABLE #fn_vtblEmployeeList_Bydate
	END
	INSERT INTO tblReportEmployeeInfo (Month,Year,Working,Terminated,Maternity,BeforeMaternity,NewHire) 
	SELECT Month,Year,Working,Terminated,Maternity,BeforeMaternity,NewHire FROM #ReportEmployeeInfo
GO
EXEC sptblReportEmployeeInfo 2022
