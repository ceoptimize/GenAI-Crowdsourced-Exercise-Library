WITH MaxVotes AS (
            SELECT MAX(GPTVotes) AS MaxGPTVotes
            FROM JointJointMovement
        ), ConfidenceScores AS (
            SELECT
                main_table.JointJointMovementID,
                main_table.GPTVotes,
                (SELECT MaxGPTVotes FROM MaxVotes) - main_table.GPTVotes AS ZeroCount,
                jsonb_array_elements(main_table.GPTLog)->>'confidence_score' AS confidence_score
            FROM 
                JointJointMovement main_table
        ), Averages AS (
            SELECT
                cs.JointJointMovementID,
                (SUM(cs.confidence_score::numeric) + (cs.ZeroCount * 0)) / (SELECT MaxGPTVotes FROM MaxVotes) AS AverageConfidence,
                (SELECT MaxGPTVotes FROM MaxVotes) AS MaxGPTVotes,
                cs.GPTVotes
            FROM 
                ConfidenceScores cs
            GROUP BY 
                cs.JointJointMovementID, cs.GPTVotes, cs.ZeroCount
        )
        SELECT 
            main_table.JointJointMovementID,
            main_table.CreatorGenerated,
            join_table1.Joint AS JoinTable1Display,
            join_table2.JointMovement AS JoinTable2Display,
            av.GPTVotes,
            av.MaxGPTVotes,
            av.AverageConfidence AS AdjustedGPTConfidence,
            main_table.GPTLog AS OriginalGPTLog
        FROM 
            JointJointMovement main_table
        JOIN 
            Joint join_table1 ON main_table.JointID = join_table1.JointID
        JOIN 
            JointMovement join_table2 ON main_table.JointMovementID = join_table2.JointMovementID
        LEFT JOIN 
            Averages av ON main_table.JointJointMovementID = av.JointJointMovementID
        ORDER BY av.AverageConfidence DESC