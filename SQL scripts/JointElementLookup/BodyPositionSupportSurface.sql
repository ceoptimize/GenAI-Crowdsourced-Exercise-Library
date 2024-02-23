
SELECT 
    ssbp.SupportSurfaceBodyPositionID,
	ssbp.CreatorGenerated,
    ssbp.GPTConfidence,
	ssbp.GPTVotes,
	ssbp.GPTLog,
    ss.SupportSurface,
    bp.BodyPosition
FROM 
    SupportSurfaceBodyPosition ssbp
JOIN 
    SupportSurface ss ON ssbp.SupportSurfaceID = ss.SupportSurfaceID
JOIN 
    BodyPosition bp ON ssbp.BodyPositionID = bp.BodyPositionID

