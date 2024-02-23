WITH MaxVotes AS (
            SELECT MAX(GPTVotes) AS MaxGPTVotes FROM JointJointMovement
        ), ConfidenceScores AS (
            SELECT
                JointJointMovementID AS ID,
                GPTVotes,
                (SELECT MaxGPTVotes FROM MaxVotes) - GPTVotes AS ZeroCount,
                jsonb_array_elements(GPTLog)->>'confidence_score' AS confidence_score
            FROM 
                JointJointMovement
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
            JointJointMovementID,
            CreatorGenerated,
            jt1.Joint AS JoinTable1Display,
            jt2.JointMovement AS JoinTable2Display,
            av.GPTVotes,
            av.MaxGPTVotes,
            av.AverageConfidence AS AdjustedGPTConfidence,
            GPTLog AS OriginalGPTLog
        FROM 
            JointJointMovement
        JOIN 
            Joint jt1 ON JointID = jt1.JointID
        JOIN 
            JointMovement jt2 ON JointMovementID = jt2.JointMovementID
        LEFT JOIN 
            Averages av ON JointJointMovementID = av.ID
        ORDER BY av.AverageConfidence DESC