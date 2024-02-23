;
CREATE TABLE "GPTLog" (
    "GPTLogID" SERIAL   NOT NULL,
    "Datetime" TIMESTAMP   NOT NULL,
    "GPTEngine" VARCHAR(50)   NOT NULL,
    "Attribute1Type" VARCHAR(50)   NOT NULL,
    "Attribute1" VARCHAR(50)   NOT NULL,
    "Attribute2Type" VARCHAR(50)   NOT NULL,
    "Attribute2" VARCHAR(50)   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    CONSTRAINT "pk_GPTLog" PRIMARY KEY (
        "GPTLogID"
     )
);

CREATE TABLE "Exercises" (
    "ExerciseID" SERIAL   NOT NULL,
    "ExerciseName" VARCHAR(50)   NOT NULL,
    "ExerciseDifficultySum" float8   NOT NULL,
    "ExerciseDifficultyCount" int   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_Exercises" PRIMARY KEY (
        "ExerciseID"
     )
);

CREATE TABLE "Equipment" (
    "EquipmentID" SERIAL   NOT NULL,
    "EquipmentName" VARCHAR(50)   NOT NULL,
    "EquipmentImageURL" VARCHAR(50)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_Equipment" PRIMARY KEY (
        "EquipmentID"
     )
);

CREATE TABLE "EquipmentType" (
    "EquipmentTypeID" SERIAL   NOT NULL,
    "EquipmentType" VARCHAR(50)   NOT NULL,
    "EquipmentTypeDescription" VARCHAR(50)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_EquipmentType" PRIMARY KEY (
        "EquipmentTypeID"
     )
);

CREATE TABLE "BodyPlane" (
    "BodyPlaneID" SERIAL   NOT NULL,
    "BodyPlane" VARCHAR(20)   NOT NULL,
    "BodyPlaneDescription" VARCHAR(50)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_BodyPlane" PRIMARY KEY (
        "BodyPlaneID"
     )
);

CREATE TABLE "BodyRegion" (
    "BodyRegionID" SERIAL   NOT NULL,
    "BodyRegion" VARCHAR(20)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_BodyRegion" PRIMARY KEY (
        "BodyRegionID"
     )
);

CREATE TABLE "BodyArea" (
    "BodyAreaID" SERIAL   NOT NULL,
    "BodyArea" VARCHAR(20)   NOT NULL,
    "BodyAreaImageURL" VARCHAR(50)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_BodyArea" PRIMARY KEY (
        "BodyAreaID"
     )
);

CREATE TABLE "BodyStructure" (
    "BodyStructureID" SERIAL   NOT NULL,
    "BodyStructure" VARCHAR(20)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_BodyStructure" PRIMARY KEY (
        "BodyStructureID"
     )
);

CREATE TABLE "Muscle" (
    "MuscleID" SERIAL   NOT NULL,
    "Muscle" VARCHAR(50)   NOT NULL,
    "BodyArea" int   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_Muscle" PRIMARY KEY (
        "MuscleID"
     )
);

CREATE TABLE "MuscleRole" (
    "MuscleRoleID" SERIAL   NOT NULL,
    "MuscleRole" VARCHAR(20)   NOT NULL,
    "MuscleRoleDescription" VARCHAR(50)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_MuscleRole" PRIMARY KEY (
        "MuscleRoleID"
     )
);

CREATE TABLE "Joint" (
    "JointID" SERIAL   NOT NULL,
    "Joint" VARCHAR(50)   NOT NULL,
    "BodyArea" int   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_Joint" PRIMARY KEY (
        "JointID"
     )
);

CREATE TABLE "JointMovement" (
    "JointMovementID" SERIAL   NOT NULL,
    "JointMovement" VARCHAR(50)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_JointMovement" PRIMARY KEY (
        "JointMovementID"
     )
);

CREATE TABLE "JointUsage" (
    "JointUsageID" SERIAL   NOT NULL,
    "JointUsage" VARCHAR(20)   NOT NULL,
    "JointUsageDescription" VARCHAR(50)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_JointUsage" PRIMARY KEY (
        "JointUsageID"
     )
);

CREATE TABLE "Utility" (
    "UtilityID" SERIAL   NOT NULL,
    "Utility" VARCHAR(20)   NOT NULL,
    "UtilityDescription" VARCHAR(50)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_Utility" PRIMARY KEY (
        "UtilityID"
     )
);

CREATE TABLE "Sides" (
    "SidesID" SERIAL   NOT NULL,
    "SidesName" VARCHAR(20)   NOT NULL,
    "SidesDescription" VARCHAR(50)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_Sides" PRIMARY KEY (
        "SidesID"
     )
);

CREATE TABLE "Measurement" (
    "MeasurementID" SERIAL   NOT NULL,
    "Measurement" VARCHAR(20)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_Measurement" PRIMARY KEY (
        "MeasurementID"
     )
);

CREATE TABLE "Chain" (
    "ChainID" SERIAL   NOT NULL,
    "Chain" VARCHAR(20)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_Chain" PRIMARY KEY (
        "ChainID"
     )
);

CREATE TABLE "OPT" (
    "OptID" SERIAL   NOT NULL,
    "OptPhase" VARCHAR(20)   NOT NULL,
    "OptPhaseDescription" VARCHAR(50)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_OPT" PRIMARY KEY (
        "OptID"
     )
);

CREATE TABLE "Category" (
    "CategoryID" SERIAL   NOT NULL,
    "CategoryName" VARCHAR(20)   NOT NULL,
    "CategoryDescription" VARCHAR(50)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_Category" PRIMARY KEY (
        "CategoryID"
     )
);

CREATE TABLE "Focus" (
    "FocusID" SERIAL   NOT NULL,
    "FocusName" VARCHAR(20)   NOT NULL,
    "FocusDescription" VARCHAR(50)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_Focus" PRIMARY KEY (
        "FocusID"
     )
);

CREATE TABLE "BodyPosition" (
    "BodyPositionID" SERIAL   NOT NULL,
    "BodyPosition" VARCHAR(50)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_BodyPosition" PRIMARY KEY (
        "BodyPositionID"
     )
);

CREATE TABLE "SupportSurface" (
    "SupportSurfaceID" SERIAL   NOT NULL,
    "SupportSurface" VARCHAR(50)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_SupportSurface" PRIMARY KEY (
        "SupportSurfaceID"
     )
);

CREATE TABLE "Corrective" (
    "CorrectiveID" SERIAL   NOT NULL,
    "CorrectiveName" VARCHAR(20)   NOT NULL,
    "CorrectiveDescription" VARCHAR(50)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_Corrective" PRIMARY KEY (
        "CorrectiveID"
     )
);

CREATE TABLE "Compensation" (
    "CompensationID" SERIAL   NOT NULL,
    "Compensation" VARCHAR(100)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_Compensation" PRIMARY KEY (
        "CompensationID"
     )
);

CREATE TABLE "Contraindication" (
    "ContraindicationID" SERIAL   NOT NULL,
    "ContraindicationName" VARCHAR(50)   NOT NULL,
    "ContraindicationDescription" VARCHAR(50)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_Contraindication" PRIMARY KEY (
        "ContraindicationID"
     )
);

CREATE TABLE "Injury" (
    "InjuryID" SERIAL   NOT NULL,
    "Injury" VARCHAR(50)   NOT NULL,
    "Type" VARCHAR(20)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_Injury" PRIMARY KEY (
        "InjuryID"
     )
);

CREATE TABLE "HealthCondition" (
    "HealthConditionID" SERIAL   NOT NULL,
    "HealthCondition" VARCHAR(50)   NOT NULL,
    "HealthConditionDescription" VARCHAR(50)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_HealthCondition" PRIMARY KEY (
        "HealthConditionID"
     )
);

CREATE TABLE "Sport" (
    "SportID" SERIAL   NOT NULL,
    "SportName" VARCHAR(50)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_Sport" PRIMARY KEY (
        "SportID"
     )
);

CREATE TABLE "Characteristic" (
    "CharacteristicID" SERIAL   NOT NULL,
    "Characteristic" VARCHAR(50)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_Characteristic" PRIMARY KEY (
        "CharacteristicID"
     )
);

CREATE TABLE "AdjustmentArea" (
    "AdjustmentAreaID" SERIAL   NOT NULL,
    "AdjustmentArea" VARCHAR(50)   NOT NULL,
    "AdjustmentAreaDescription" VARCHAR(50)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_AdjustmentArea" PRIMARY KEY (
        "AdjustmentAreaID"
     )
);

CREATE TABLE "YoutubeVideo" (
    "VideoID" VARCHAR(50)   NOT NULL,
    "VideoTitle" VARCHAR(255)   NOT NULL,
    "Likes" int   NOT NULL,
    "ChannelID" VARCHAR(100)   NOT NULL,
    "ChannelName" VARCHAR(100)   NOT NULL,
    "ChannelHandle" VARCHAR(100)   NOT NULL,
    "Subscribers" int   NOT NULL,
    "ThumbnailUrl" VARCHAR(100)   NOT NULL,
    "Captions" TEXT   NOT NULL,
    "Duration" int   NOT NULL,
    "GenderCount" int   NOT NULL,
    "Lighting" int   NOT NULL,
    "Audio" int   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_YoutubeVideo" PRIMARY KEY (
        "VideoID"
     )
);

CREATE TABLE "ExerciseDescription" (
    "ExerciseDescriptionID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "ExerciseDescription" TEXT   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_ExerciseDescription" PRIMARY KEY (
        "ExerciseDescriptionID"
     )
);

CREATE TABLE "ExerciseTag" (
    "ExerciseTagID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "ExerciseTag" VARCHAR(50)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_ExerciseTag" PRIMARY KEY (
        "ExerciseTagID"
     )
);

CREATE TABLE "ExerciseBodyArea" (
    "ExerciseBodyAreaID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "BodyAreaID" int   NOT NULL,
    "IsPrimary" boolean   NOT NULL,
    "IsPrimaryVotes" int   NOT NULL,
    "IsSecondary" boolean   NOT NULL,
    "IsSecondaryVotes" int   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_ExerciseBodyArea" PRIMARY KEY (
        "ExerciseBodyAreaID"
     )
);

CREATE TABLE "ExerciseJointUsage" (
    "ExerciseJointUsageID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "JointUsageID" int   NOT NULL,
    "JointUsageVotes" int   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_ExerciseJointUsage" PRIMARY KEY (
        "ExerciseJointUsageID"
     )
);

CREATE TABLE "ExerciseSides" (
    "ExerciseSidesID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "SidesID" int   NOT NULL,
    "SidesVotes" int   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_ExerciseSides" PRIMARY KEY (
        "ExerciseSidesID"
     )
);

CREATE TABLE "ExerciseOPT" (
    "ExerciseOptID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "OptID" int   NOT NULL,
    "OptVotes" int   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_ExerciseOPT" PRIMARY KEY (
        "ExerciseOptID"
     )
);

CREATE TABLE "ExerciseCategory" (
    "ExerciseCategoryID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "CategoryID" int   NOT NULL,
    "CategoryVotes" int   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_ExerciseCategory" PRIMARY KEY (
        "ExerciseCategoryID"
     )
);

CREATE TABLE "ExerciseCorrective" (
    "ExerciseCorrectiveID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "CorrectiveID" int   NOT NULL,
    "CorrectiveVotes" int   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_ExerciseCorrective" PRIMARY KEY (
        "ExerciseCorrectiveID"
     )
);

CREATE TABLE "ExerciseContraindication" (
    "ExerciseContraindicationID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "ContraindicationID" int   NOT NULL,
    "ContraindicationVotes" int   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_ExerciseContraindication" PRIMARY KEY (
        "ExerciseContraindicationID"
     )
);

CREATE TABLE "ExerciseSport" (
    "ExerciseSportID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "SportID" int   NOT NULL,
    "SportVotes" int   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_ExerciseSport" PRIMARY KEY (
        "ExerciseSportID"
     )
);

CREATE TABLE "ExerciseEquipment" (
    "ExerciseEquipmentID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "EquipmentID" int   NOT NULL,
    "Count" int   NOT NULL,
    "CountVotes" int   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_ExerciseEquipment" PRIMARY KEY (
        "ExerciseEquipmentID"
     )
);

CREATE TABLE "ExercisePlane" (
    "ExercisePlaneID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "BodyPlaneID" int   NOT NULL,
    "PlaneVotes" int   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_ExercisePlane" PRIMARY KEY (
        "ExercisePlaneID"
     )
);

CREATE TABLE "ExerciseYoutube" (
    "ExerciseYoutubeID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "YoutubeVideoID" VARCHAR(20)   NOT NULL,
    "ExerciseVideoMatch" int   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_ExerciseYoutube" PRIMARY KEY (
        "ExerciseYoutubeID"
     )
);

CREATE TABLE "ExerciseRelation" (
    "ExerciseRelationID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "RelationID" int   NOT NULL,
    "RelationType" VARCHAR(20)   NOT NULL,
    "RelationVotes" int   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_ExerciseRelation" PRIMARY KEY (
        "ExerciseRelationID"
     )
);

CREATE TABLE "MuscleRelation" (
    "MuscleRelationID" SERIAL   NOT NULL,
    "MuscleID" int   NOT NULL,
    "RelationID" int   NOT NULL,
    "RelationType" VARCHAR(20)   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_MuscleRelation" PRIMARY KEY (
        "MuscleRelationID"
     )
);

CREATE TABLE "ExerciseRelationDetail" (
    "ExerciseRelationDetailID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "RelationID" int   NOT NULL,
    "RelationType" VARCHAR(20)   NOT NULL,
    "AdjustmentType" VARCHAR(50)   NOT NULL,
    "RelationDetailVotes" int   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_ExerciseRelationDetail" PRIMARY KEY (
        "ExerciseRelationDetailID"
     )
);

CREATE TABLE "ExerciseNameAlias" (
    "ExerciseAliasID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "AliasID" int   NOT NULL,
    "AliasVotes" int   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_ExerciseNameAlias" PRIMARY KEY (
        "ExerciseAliasID"
     )
);

CREATE TABLE "SupportSurfaceBodyPosition" (
    "SupportSurfaceBodyPositionID" SERIAL   NOT NULL,
    "SupportSurfaceID" int   NOT NULL,
    "BodyPositionID" int   NOT NULL,
    "CreatorGenerated" boolean   NOT NULL,
    "GPTVotes" int   NOT NULL,
    "GPTConfidence" float8   NOT NULL,
    "GPTLog" JSONB   NOT NULL,
    CONSTRAINT "pk_SupportSurfaceBodyPosition" PRIMARY KEY (
        "SupportSurfaceBodyPositionID"
     )
);

ALTER TABLE "Muscle" ADD CONSTRAINT "fk_Muscle_BodyArea" FOREIGN KEY("BodyArea")
REFERENCES "BodyArea" ("BodyAreaID");

ALTER TABLE "Joint" ADD CONSTRAINT "fk_Joint_BodyArea" FOREIGN KEY("BodyArea")
REFERENCES "BodyArea" ("BodyAreaID");

ALTER TABLE "ExerciseDescription" ADD CONSTRAINT "fk_ExerciseDescription_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseTag" ADD CONSTRAINT "fk_ExerciseTag_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseBodyArea" ADD CONSTRAINT "fk_ExerciseBodyArea_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseBodyArea" ADD CONSTRAINT "fk_ExerciseBodyArea_BodyAreaID" FOREIGN KEY("BodyAreaID")
REFERENCES "BodyArea" ("BodyAreaID");

ALTER TABLE "ExerciseJointUsage" ADD CONSTRAINT "fk_ExerciseJointUsage_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseJointUsage" ADD CONSTRAINT "fk_ExerciseJointUsage_JointUsageID" FOREIGN KEY("JointUsageID")
REFERENCES "JointUsage" ("JointUsageID");

ALTER TABLE "ExerciseSides" ADD CONSTRAINT "fk_ExerciseSides_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseSides" ADD CONSTRAINT "fk_ExerciseSides_SidesID" FOREIGN KEY("SidesID")
REFERENCES "Sides" ("SidesID");

ALTER TABLE "ExerciseOPT" ADD CONSTRAINT "fk_ExerciseOPT_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseOPT" ADD CONSTRAINT "fk_ExerciseOPT_OptID" FOREIGN KEY("OptID")
REFERENCES "OPT" ("OptID");

ALTER TABLE "ExerciseCategory" ADD CONSTRAINT "fk_ExerciseCategory_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseCategory" ADD CONSTRAINT "fk_ExerciseCategory_CategoryID" FOREIGN KEY("CategoryID")
REFERENCES "Category" ("CategoryID");

ALTER TABLE "ExerciseCorrective" ADD CONSTRAINT "fk_ExerciseCorrective_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseCorrective" ADD CONSTRAINT "fk_ExerciseCorrective_CorrectiveID" FOREIGN KEY("CorrectiveID")
REFERENCES "Corrective" ("CorrectiveID");

ALTER TABLE "ExerciseContraindication" ADD CONSTRAINT "fk_ExerciseContraindication_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseContraindication" ADD CONSTRAINT "fk_ExerciseContraindication_ContraindicationID" FOREIGN KEY("ContraindicationID")
REFERENCES "Contraindication" ("ContraindicationID");

ALTER TABLE "ExerciseSport" ADD CONSTRAINT "fk_ExerciseSport_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseSport" ADD CONSTRAINT "fk_ExerciseSport_SportID" FOREIGN KEY("SportID")
REFERENCES "Sport" ("SportID");

ALTER TABLE "ExerciseEquipment" ADD CONSTRAINT "fk_ExerciseEquipment_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseEquipment" ADD CONSTRAINT "fk_ExerciseEquipment_EquipmentID" FOREIGN KEY("EquipmentID")
REFERENCES "Equipment" ("EquipmentID");

ALTER TABLE "ExercisePlane" ADD CONSTRAINT "fk_ExercisePlane_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExercisePlane" ADD CONSTRAINT "fk_ExercisePlane_BodyPlaneID" FOREIGN KEY("BodyPlaneID")
REFERENCES "BodyPlane" ("BodyPlaneID");

ALTER TABLE "ExerciseYoutube" ADD CONSTRAINT "fk_ExerciseYoutube_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseYoutube" ADD CONSTRAINT "fk_ExerciseYoutube_YoutubeVideoID" FOREIGN KEY("YoutubeVideoID")
REFERENCES "YoutubeVideo" ("VideoID");

ALTER TABLE "ExerciseRelation" ADD CONSTRAINT "fk_ExerciseRelation_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseRelation" ADD CONSTRAINT "fk_ExerciseRelation_RelationID" FOREIGN KEY("RelationID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "MuscleRelation" ADD CONSTRAINT "fk_MuscleRelation_MuscleID" FOREIGN KEY("MuscleID")
REFERENCES "Muscle" ("MuscleID");

ALTER TABLE "MuscleRelation" ADD CONSTRAINT "fk_MuscleRelation_RelationID" FOREIGN KEY("RelationID")
REFERENCES "Muscle" ("MuscleID");

ALTER TABLE "ExerciseRelationDetail" ADD CONSTRAINT "fk_ExerciseRelationDetail_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseRelationDetail" ADD CONSTRAINT "fk_ExerciseRelationDetail_RelationID" FOREIGN KEY("RelationID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseNameAlias" ADD CONSTRAINT "fk_ExerciseNameAlias_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseNameAlias" ADD CONSTRAINT "fk_ExerciseNameAlias_AliasID" FOREIGN KEY("AliasID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "SupportSurfaceBodyPosition" ADD CONSTRAINT "fk_SupportSurfaceBodyPosition_SupportSurfaceID" FOREIGN KEY("SupportSurfaceID")
REFERENCES "SupportSurface" ("SupportSurfaceID");

ALTER TABLE "SupportSurfaceBodyPosition" ADD CONSTRAINT "fk_SupportSurfaceBodyPosition_BodyPositionID" FOREIGN KEY("BodyPositionID")
REFERENCES "BodyPosition" ("BodyPositionID");

CREATE INDEX "idx_GPTLog_Attribute1Type"
ON "GPTLog" ("Attribute1Type");

CREATE INDEX "idx_GPTLog_Attribute1"
ON "GPTLog" ("Attribute1");

CREATE INDEX "idx_GPTLog_Attribute2Type"
ON "GPTLog" ("Attribute2Type");

CREATE INDEX "idx_GPTLog_Attribute2"
ON "GPTLog" ("Attribute2");

CREATE INDEX "idx_Exercises_ExerciseName"
ON "Exercises" ("ExerciseName");

CREATE INDEX "idx_Equipment_EquipmentName"
ON "Equipment" ("EquipmentName");

CREATE INDEX "idx_EquipmentType_EquipmentType"
ON "EquipmentType" ("EquipmentType");

CREATE INDEX "idx_BodyPlane_BodyPlane"
ON "BodyPlane" ("BodyPlane");

CREATE INDEX "idx_BodyRegion_BodyRegion"
ON "BodyRegion" ("BodyRegion");

CREATE INDEX "idx_BodyArea_BodyArea"
ON "BodyArea" ("BodyArea");

CREATE INDEX "idx_BodyStructure_BodyStructure"
ON "BodyStructure" ("BodyStructure");

CREATE INDEX "idx_Muscle_Muscle"
ON "Muscle" ("Muscle");

CREATE INDEX "idx_MuscleRole_MuscleRole"
ON "MuscleRole" ("MuscleRole");

CREATE INDEX "idx_Joint_Joint"
ON "Joint" ("Joint");

CREATE INDEX "idx_JointMovement_JointMovement"
ON "JointMovement" ("JointMovement");

CREATE INDEX "idx_JointUsage_JointUsage"
ON "JointUsage" ("JointUsage");

CREATE INDEX "idx_Utility_Utility"
ON "Utility" ("Utility");

CREATE INDEX "idx_Sides_SidesName"
ON "Sides" ("SidesName");

CREATE INDEX "idx_Measurement_Measurement"
ON "Measurement" ("Measurement");

CREATE INDEX "idx_Chain_Chain"
ON "Chain" ("Chain");

CREATE INDEX "idx_OPT_OptPhase"
ON "OPT" ("OptPhase");

CREATE INDEX "idx_Category_CategoryName"
ON "Category" ("CategoryName");

CREATE INDEX "idx_Focus_FocusName"
ON "Focus" ("FocusName");

CREATE INDEX "idx_BodyPosition_BodyPosition"
ON "BodyPosition" ("BodyPosition");

CREATE INDEX "idx_SupportSurface_SupportSurface"
ON "SupportSurface" ("SupportSurface");

CREATE INDEX "idx_Corrective_CorrectiveName"
ON "Corrective" ("CorrectiveName");

CREATE INDEX "idx_Compensation_Compensation"
ON "Compensation" ("Compensation");

CREATE INDEX "idx_Contraindication_ContraindicationName"
ON "Contraindication" ("ContraindicationName");

CREATE INDEX "idx_HealthCondition_HealthCondition"
ON "HealthCondition" ("HealthCondition");

CREATE INDEX "idx_Sport_SportName"
ON "Sport" ("SportName");

CREATE INDEX "idx_Characteristic_Characteristic"
ON "Characteristic" ("Characteristic");

CREATE INDEX "idx_AdjustmentArea_AdjustmentArea"
ON "AdjustmentArea" ("AdjustmentArea");

