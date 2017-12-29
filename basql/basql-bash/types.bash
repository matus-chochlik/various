function UID()
{
	echo "BIGINT"
}

function ID()
{
	echo "INTEGER"
}

function SID()
{
	echo "SMALLINT"
}

function SNP_ID()
{
	echo "INTEGER"
}

function STR_CODE()
{
	length=${1:-8}
	echo "VARCHAR(${length})"
}

function TINYINT()
{
	echo "SMALLINT"
}

function STRING()
{
	echo "VARCHAR(${1})"
}

function NAME_STR()
{
	echo "VARCHAR(50)"
}

function DESC_STR()
{
	echo "VARCHAR(500)"
}

function FUNCTION_RESULT_KIND()
{
	echo "CHAR(1)"
}

function FUNCTION_PARAM_KIND()
{
	echo "CHAR(1)"
}

function PASSWD_STR()
{
	echo "CHAR(60)"
}

function COUNTRY_CODE()
{
	echo "VARCHAR(3)"
}

function LOCALE_CODE()
{
	echo "VARCHAR(7)"
}

function FLOAT()
{
	echo "REAL"
}

function DATE()
{
	echo "DATE"
}

function DATE_TIME()
{
	echo "TIMESTAMP WITH TIME ZONE"
}

function BOOLEAN()
{
	echo "BOOLEAN"
}

function TRUE()
{
	echo "true"
}

function FALSE()
{
	echo "false"
}

function LOGIN_NAME()
{
	echo "VARCHAR(24)"
}

function BACKEND_ID()
{
	echo "INTEGER"
}

function SQL_IDENTIFIER()
{
	echo "INFORMATION_SCHEMA.SQL_IDENTIFIER"
}

function DATA_TYPE()
{
	echo "INFORMATION_SCHEMA.CHARACTER_DATA"
}

function CARDINAL_NUMBER()
{
	echo "INFORMATION_SCHEMA.CARDINAL_NUMBER"
}

function OPERATION_NAME()
{
	echo "CHAR(6)"
}

function NUCLEIC_ACID_CODE()
{
	echo "CHAR(4)"
}

function NUCLEOBASE_CODE()
{
	echo "CHAR(1)"
}

function AMINO_ACID_CODE()
{
	echo "CHAR(1)"
}

function GENOTYPE_CODE()
{
	echo "CHAR(2)"
}

function ANY_ALLELE()
{
	echo "VARCHAR(32)"
}

function CHROMOZOME()
{
	echo "CHAR(2)"
}

function NP_REFERENCE_CODE()
{
	echo "VARCHAR(24)"
}

function GENDER_CODE()
{
	echo "CHAR(1)"
}

function DIMENSION_SPACE()
{
	echo "$(PREFIXED base_dimension_space)"
}
