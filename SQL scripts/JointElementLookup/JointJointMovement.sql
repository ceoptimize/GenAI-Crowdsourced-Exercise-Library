SELECT 
    jjm.JointJointMovementID,
    jjm.CreatorGenerated,
    jjm.GPTConfidence,
    jjm.GPTVotes,
    jjm.GPTLog,
    j.Joint AS JointName,
    jm.JointMovement AS JointMovementName
FROM 
    JointJointMovement jjm
JOIN 
    Joint j ON jjm.JointID = j.JointID
JOIN 
    JointMovement jm ON jjm.JointMovementID = jm.JointMovementID;
