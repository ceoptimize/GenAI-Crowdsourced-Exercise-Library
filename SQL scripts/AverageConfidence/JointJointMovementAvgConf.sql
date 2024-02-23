WITH MaxVotes AS (
    SELECT MAX(GPTVotes) AS MaxGPTVotes
    FROM JointJointMovement
), ConfidenceScores AS (
    SELECT
        jjm.JointJointMovementID,
        jjm.GPTVotes,
        (SELECT MaxGPTVotes FROM MaxVotes) - jjm.GPTVotes AS ZeroCount,
        jsonb_array_elements_text(jjm.GPTLog->'confidence_score') AS confidence_score
    FROM 
        JointJointMovement jjm
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
    jjm.JointJointMovementID,
    jjm.CreatorGenerated,
    j.Joint AS JointName,
    jm.JointMovement AS JointMovementName,
    av.GPTVotes,
    av.MaxGPTVotes,
    av.AverageConfidence AS AdjustedGPTConfidence,
    jjm.GPTLog AS OriginalGPTLog
FROM 
    JointJointMovement jjm
JOIN 
    Joint j ON jjm.JointID = j.JointID
JOIN 
    JointMovement jm ON jjm.JointMovementID = jm.JointMovementID
LEFT JOIN 
    Averages av ON jjm.JointJointMovementID = av.JointJointMovementID
ORDER BY av.AverageConfidence DESC;
