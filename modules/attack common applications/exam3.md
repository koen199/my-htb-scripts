# Exam3

We should decompile the `Multimaster.dll` file found at `C:\inetpub\wwwroot\bin`.
Executing the `strings` method we find string which look like this could be compiled from a .NET language.
Stuff such as:
```
.NETFramework,Version=v4.6.1
FrameworkDisplayName
.NET Framework 4.6.1
api/getColleagues
```

We decompile the code with `dnSpy` and can located the sql connection string in one of the source files


