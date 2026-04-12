from pydantic import BaseModel, Field

class EmployeeData(BaseModel):
    age: int
    businesstravel: str
    dailyrate: int
    department: str
    distancefromhome: int
    education: int = Field(description="This is the highest level of education of the employee", default="High School")
    educationfield: str
    employeecount: int
    environmentsatisfaction: int
    gender: str
    hourlyrate: int
    jobinvolvement: int
    joblevel: int
    jobrole: str
    jobsatisfaction: int
    maritalstatus: str
    monthlyincome: int
    monthlyrate: int
    numcompaniesworked: int
    over18: str
    overtime: str
    percentsalaryhike: int
    performancerating: int
    relationshipsatisfaction: int
    standardhours: int
    stockoptionlevel: int
    totalworkingyears: int
    trainingtimeslastyear: int
    worklifebalance: int
    yearsatcompany: int
    yearsincurrentrole: int
    yearssincelastpromotion: int
    yearswithcurrmanager: int
