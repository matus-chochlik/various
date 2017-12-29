function FINALIZE_SCHEMA()
{
	echo "CREATE FUNCTION $(PREFIXED synchronize_id_sequences)() RETURNS VOID"
	echo 'AS'
	echo '$$'
	echo 'DECLARE'
	echo '	cur_val BIGINT;'
	echo 'BEGIN'

	for table in $(basql_fetch_key_value TABLES_WITH_ID_SEQUENCE)
	do
		echo "cur_val := NULL;"
		echo "SELECT max($(TABLE_PK_NAME ${table}))"
		echo "INTO cur_val"
		echo "FROM $(PREFIXED ${table});"
		echo
		echo "IF cur_val IS NULL"
		echo "THEN ALTER SEQUENCE  $(PREFIXED seq_$(TABLE_PK_NAME ${table})) RESTART;"
		echo "ELSE PERFORM setval('$(PREFIXED seq_$(TABLE_PK_NAME ${table}))', cur_val);"
		echo "END IF;"
		echo
	done

	echo 'END;'
	echo '$$'
	echo 'LANGUAGE PLPGSQL;'
	echo
}

