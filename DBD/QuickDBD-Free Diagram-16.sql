;

CREATE TABLE "Exercises" (
    "ExerciseID" SERIAL   NOT NULL,
    "ExerciseName" VARCHAR(50)   NOT NULL,
    "ExerciseDifficultySum" float8   NOT NULL,
    "ExerciseDifficultyCount" int   NOT NULL,
    CONSTRAINT "pk_Exercises" PRIMARY KEY (
        "ExerciseID"
     )
);

CREATE TABLE "Equipment" (
    "EquipmentID" SERIAL   NOT NULL,
    "EquipmentName" VARCHAR(20)   NOT NULL,
    "EquipmentImageURL" VARCHAR(50)   NOT NULL,
    CONSTRAINT "pk_Equipment" PRIMARY KEY (
        "EquipmentID"
     )
);

CREATE TABLE "BodyPlane" (
    "BodyPlaneID" SERIAL   NOT NULL,
    "BodyPlane" VARCHAR(20)   NOT NULL,
    "BodyPlaneDescription" VARCHAR(50)   NOT NULL,
    CONSTRAINT "pk_BodyPlane" PRIMARY KEY (
        "BodyPlaneID"
     )
);

CREATE TABLE "BodyArea" (
    "BodyAreaID" SERIAL   NOT NULL,
    "BodyArea" VARCHAR(20)   NOT NULL,
    "BodyAreaImageURL" VARCHAR(50)   NOT NULL,
    CONSTRAINT "pk_BodyArea" PRIMARY KEY (
        "BodyAreaID"
     )
);

CREATE TABLE "Mechanics" (
    "MechanicsID" SERIAL   NOT NULL,
    "Mechanics" VARCHAR(20)   NOT NULL,
    "MechanicsDescription" VARCHAR(50)   NOT NULL,
    CONSTRAINT "pk_Mechanics" PRIMARY KEY (
        "MechanicsID"
     )
);

CREATE TABLE "JointUsage" (
    "JointUsageID" SERIAL   NOT NULL,
    "JointUsage" VARCHAR(20)   NOT NULL,
    "JointUsageDescription" VARCHAR(50)   NOT NULL,
    CONSTRAINT "pk_JointUsage" PRIMARY KEY (
        "JointUsageID"
     )
);

CREATE TABLE "Sides" (
    "SidesID" SERIAL   NOT NULL,
    "SidesName" VARCHAR(20)   NOT NULL,
    "SidesDescription" VARCHAR(50)   NOT NULL,
    CONSTRAINT "pk_Sides" PRIMARY KEY (
        "SidesID"
     )
);

CREATE TABLE "OPT" (
    "OptID" SERIAL   NOT NULL,
    "OptPhase" VARCHAR(20)   NOT NULL,
    "OptPhaseDescription" VARCHAR(50)   NOT NULL,
    CONSTRAINT "pk_OPT" PRIMARY KEY (
        "OptID"
     )
);

CREATE TABLE "Category" (
    "CategoryID" SERIAL   NOT NULL,
    "CategoryName" VARCHAR(20)   NOT NULL,
    "CategoryDescription" VARCHAR(50)   NOT NULL,
    CONSTRAINT "pk_Category" PRIMARY KEY (
        "CategoryID"
     )
);

CREATE TABLE "Corrective" (
    "CorrectiveID" SERIAL   NOT NULL,
    "CorrectiveName" VARCHAR(20)   NOT NULL,
    "CorrectiveDescription" VARCHAR(50)   NOT NULL,
    CONSTRAINT "pk_Corrective" PRIMARY KEY (
        "CorrectiveID"
     )
);

CREATE TABLE "Contraindication" (
    "ContraindicationID" SERIAL   NOT NULL,
    "ContraindicationName" VARCHAR(50)   NOT NULL,
    "ContraindicationDescription" VARCHAR(50)   NOT NULL,
    CONSTRAINT "pk_Contraindication" PRIMARY KEY (
        "ContraindicationID"
     )
);

CREATE TABLE "Sport" (
    "SportID" SERIAL   NOT NULL,
    "SportName" VARCHAR(20)   NOT NULL,
    CONSTRAINT "pk_Sport" PRIMARY KEY (
        "SportID"
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
    CONSTRAINT "pk_YoutubeVideo" PRIMARY KEY (
        "VideoID"
     )
);

CREATE TABLE "ExerciseDescription" (
    "ExerciseDescriptionID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "ExerciseDescription" TEXT   NOT NULL,
    CONSTRAINT "pk_ExerciseDescription" PRIMARY KEY (
        "ExerciseDescriptionID"
     )
);

CREATE TABLE "ExerciseTag" (
    "ExerciseTagID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "ExerciseTag" VARCHAR(50)   NOT NULL,
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
    CONSTRAINT "pk_ExerciseBodyArea" PRIMARY KEY (
        "ExerciseBodyAreaID"
     )
);

CREATE TABLE "ExerciseMechanics" (
    "ExerciseMechanicsID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "MechanicsID" int   NOT NULL,
    "MechanicsVotes" int   NOT NULL,
    CONSTRAINT "pk_ExerciseMechanics" PRIMARY KEY (
        "ExerciseMechanicsID"
     )
);

CREATE TABLE "ExerciseJointUsage" (
    "ExerciseJointUsageID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "JointUsageID" int   NOT NULL,
    "JointUsageVotes" int   NOT NULL,
    CONSTRAINT "pk_ExerciseJointUsage" PRIMARY KEY (
        "ExerciseJointUsageID"
     )
);

CREATE TABLE "ExerciseSides" (
    "ExerciseSidesID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "SidesID" int   NOT NULL,
    "SidesVotes" int   NOT NULL,
    CONSTRAINT "pk_ExerciseSides" PRIMARY KEY (
        "ExerciseSidesID"
     )
);

CREATE TABLE "ExerciseOPT" (
    "ExerciseOptID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "OptID" int   NOT NULL,
    "OptVotes" int   NOT NULL,
    CONSTRAINT "pk_ExerciseOPT" PRIMARY KEY (
        "ExerciseOptID"
     )
);

CREATE TABLE "ExerciseCategory" (
    "ExerciseCategoryID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "CategoryID" int   NOT NULL,
    "CategoryVotes" int   NOT NULL,
    CONSTRAINT "pk_ExerciseCategory" PRIMARY KEY (
        "ExerciseCategoryID"
     )
);

CREATE TABLE "ExerciseCorrective" (
    "ExerciseCorrectiveID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "CorrectiveID" int   NOT NULL,
    "CorrectiveVotes" int   NOT NULL,
    CONSTRAINT "pk_ExerciseCorrective" PRIMARY KEY (
        "ExerciseCorrectiveID"
     )
);

CREATE TABLE "ExerciseContraindication" (
    "ExerciseContraindicationID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "ContraindicationID" int   NOT NULL,
    "ContraindicationVotes" int   NOT NULL,
    CONSTRAINT "pk_ExerciseContraindication" PRIMARY KEY (
        "ExerciseContraindicationID"
     )
);

CREATE TABLE "ExerciseSport" (
    "ExerciseSportID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "SportID" int   NOT NULL,
    "SportVotes" int   NOT NULL,
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
    CONSTRAINT "pk_ExerciseEquipment" PRIMARY KEY (
        "ExerciseEquipmentID"
     )
);

CREATE TABLE "ExercisePlane" (
    "ExercisePlaneID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "BodyPlaneID" int   NOT NULL,
    "PlaneVotes" int   NOT NULL,
    CONSTRAINT "pk_ExercisePlane" PRIMARY KEY (
        "ExercisePlaneID"
     )
);

CREATE TABLE "ExerciseYoutube" (
    "ExerciseYoutubeID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "YoutubeVideoID" VARCHAR(20)   NOT NULL,
    "ExerciseVideoMatch" int   NOT NULL,
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
    CONSTRAINT "pk_ExerciseRelation" PRIMARY KEY (
        "ExerciseRelationID"
     )
);

CREATE TABLE "ExerciseRelationDetail" (
    "ExerciseRelationDetailID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "RelationID" int   NOT NULL,
    "RelationType" VARCHAR(20)   NOT NULL,
    "AdjustmentType" VARCHAR(50)   NOT NULL,
    "RelationDetailVotes" int   NOT NULL,
    CONSTRAINT "pk_ExerciseRelationDetail" PRIMARY KEY (
        "ExerciseRelationDetailID"
     )
);

CREATE TABLE "ExerciseNameAlias" (
    "ExerciseAliasID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "AliasID" int   NOT NULL,
    "AliasVotes" int   NOT NULL,
    CONSTRAINT "pk_ExerciseNameAlias" PRIMARY KEY (
        "ExerciseAliasID"
     )
);

ALTER TABLE "ExerciseDescription" ADD CONSTRAINT "fk_ExerciseDescription_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseTag" ADD CONSTRAINT "fk_ExerciseTag_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseBodyArea" ADD CONSTRAINT "fk_ExerciseBodyArea_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseBodyArea" ADD CONSTRAINT "fk_ExerciseBodyArea_BodyAreaID" FOREIGN KEY("BodyAreaID")
REFERENCES "BodyArea" ("BodyAreaID");

ALTER TABLE "ExerciseMechanics" ADD CONSTRAINT "fk_ExerciseMechanics_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseMechanics" ADD CONSTRAINT "fk_ExerciseMechanics_MechanicsID" FOREIGN KEY("MechanicsID")
REFERENCES "Mechanics" ("MechanicsID");

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

ALTER TABLE "ExerciseRelationDetail" ADD CONSTRAINT "fk_ExerciseRelationDetail_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseRelationDetail" ADD CONSTRAINT "fk_ExerciseRelationDetail_RelationID" FOREIGN KEY("RelationID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseNameAlias" ADD CONSTRAINT "fk_ExerciseNameAlias_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseNameAlias" ADD CONSTRAINT "fk_ExerciseNameAlias_AliasID" FOREIGN KEY("AliasID")
REFERENCES "Exercises" ("ExerciseID");

CREATE INDEX "idx_Exercises_ExerciseName"
ON "Exercises" ("ExerciseName");

CREATE INDEX "idx_Equipment_EquipmentName"
ON "Equipment" ("EquipmentName");

CREATE INDEX "idx_BodyPlane_BodyPlane"
ON "BodyPlane" ("BodyPlane");

CREATE INDEX "idx_BodyArea_BodyArea"
ON "BodyArea" ("BodyArea");

CREATE INDEX "idx_Mechanics_Mechanics"
ON "Mechanics" ("Mechanics");

CREATE INDEX "idx_JointUsage_JointUsage"
ON "JointUsage" ("JointUsage");

CREATE INDEX "idx_Sides_SidesName"
ON "Sides" ("SidesName");

CREATE INDEX "idx_OPT_OptPhase"
ON "OPT" ("OptPhase");

CREATE INDEX "idx_Category_CategoryName"
ON "Category" ("CategoryName");

CREATE INDEX "idx_Corrective_CorrectiveName"
ON "Corrective" ("CorrectiveName");

CREATE INDEX "idx_Contraindication_ContraindicationName"
ON "Contraindication" ("ContraindicationName");

CREATE INDEX "idx_Sport_SportName"
ON "Sport" ("SportName");

