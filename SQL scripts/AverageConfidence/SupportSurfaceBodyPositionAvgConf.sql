WITH MaxVotes AS (
    SELECT MAX(GPTVotes) AS MaxGPTVotes
    FROM SupportSurfaceBodyPosition
), ConfidenceScores AS (
    SELECT
        ssbp.SupportSurfaceBodyPositionID,
        ssbp.GPTVotes,
        (SELECT MaxGPTVotes FROM MaxVotes) - ssbp.GPTVotes AS ZeroCount,
        jsonb_array_elements(ssbp.GPTLog)->>'confidence_score' AS confidence_score
    FROM 
        SupportSurfaceBodyPosition ssbp
), Averages AS (
    SELECT
        cs.SupportSurfaceBodyPositionID,
        (SUM(cs.confidence_score::numeric) + (cs.ZeroCount * 0)) / (SELECT MaxGPTVotes FROM MaxVotes) AS AverageConfidence,
        (SELECT MaxGPTVotes FROM MaxVotes) AS MaxGPTVotes,
        cs.GPTVotes
    FROM 
        ConfidenceScores cs
    GROUP BY 
        cs.SupportSurfaceBodyPositionID, cs.GPTVotes, cs.ZeroCount
)
SELECT 
    ssbp.SupportSurfaceBodyPositionID,
    ssbp.CreatorGenerated,
    ss.SupportSurface,
    bp.BodyPosition,
    av.GPTVotes,
    av.MaxGPTVotes,
    av.AverageConfidence AS AdjustedGPTConfidence,
    ssbp.GPTLog AS OriginalGPTLog
FROM 
    SupportSurfaceBodyPosition ssbp
JOIN 
    SupportSurface ss ON ssbp.SupportSurfaceID = ss.SupportSurfaceID
JOIN 
    BodyPosition bp ON ssbp.BodyPositionID = bp.BodyPositionID
LEFT JOIN 
    Averages av ON ssbp.SupportSurfaceBodyPositionID = av.SupportSurfaceBodyPositionID
order by av.AverageConfidence DESC