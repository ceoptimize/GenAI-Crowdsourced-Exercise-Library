CREATE OR REPLACE FUNCTION generate_dynamic_confidence_view_new(
    main_table_name TEXT,
    main_table_id_column TEXT,
    main_table_fk_column1 TEXT,
    main_table_fk_column2 TEXT,
    join_table1_name TEXT,
    join_table1_id_column TEXT,
    join_table1_display_column TEXT,
    join_table2_name TEXT,
    join_table2_id_column TEXT,
    join_table2_display_column TEXT
) RETURNS TEXT AS $$
DECLARE
    dynamic_sql TEXT;
BEGIN
    dynamic_sql := format($f$
        WITH MaxVotes AS (
            SELECT MAX(GPTVotes) AS MaxGPTVotes FROM %I
        ), ConfidenceScores AS (
            SELECT
                %I AS ID,
                GPTVotes,
                (SELECT MaxGPTVotes FROM MaxVotes) - GPTVotes AS ZeroCount,
                jsonb_array_elements(GPTLog)->>'confidence_score' AS confidence_score
            FROM 
                %I
        ), Averages AS (
            SELECT
                ID,
                (SUM(confidence_score::numeric) + (ZeroCount * 0)) / (SELECT MaxGPTVotes FROM MaxVotes) AS AverageConfidence,
                (SELECT MaxGPTVotes FROM MaxVotes) AS MaxGPTVotes,
                GPTVotes
            FROM 
                ConfidenceScores
            GROUP BY 
                ID, GPTVotes, ZeroCount
        )
        SELECT 
            %I,
            CreatorGenerated,
            jt1.%I AS JoinTable1Display,
            jt2.%I AS JoinTable2Display,
            av.GPTVotes,
            av.MaxGPTVotes,
            av.AverageConfidence AS AdjustedGPTConfidence,
            GPTLog AS OriginalGPTLog
        FROM 
            %I
        JOIN 
            %I jt1 ON %I = jt1.%I
        JOIN 
            %I jt2 ON %I = jt2.%I
        LEFT JOIN 
            Averages av ON %I = av.ID
        ORDER BY av.AverageConfidence DESC
    $f$, 
    main_table_name, -- FROM %I
    main_table_id_column, -- %I AS ID
    main_table_name, -- FROM %I
    main_table_id_column, -- SELECT %I,
    join_table1_display_column, -- jt1.%I AS JoinTable1Display
    join_table2_display_column, -- jt2.%I AS JoinTable2Display
    main_table_name, -- FROM %I
    join_table1_name, main_table_fk_column1, join_table1_id_column, -- JOIN %I jt1 ON %I = jt1.%I
    join_table2_name, main_table_fk_column2, join_table2_id_column, -- JOIN %I jt2 ON %I = jt2.%I
    main_table_id_column -- LEFT JOIN Averages av ON %I = av.ID
    );

    RAISE NOTICE 'Dynamic SQL: %', dynamic_sql;
    -- EXECUTE dynamic_sql;
END;
$$ LANGUAGE plpgsql;
