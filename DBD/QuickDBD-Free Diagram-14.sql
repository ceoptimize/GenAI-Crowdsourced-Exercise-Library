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

CREATE TABLE "YoutubeVideo" (
    "VideoID" VARCHAR(50)   NOT NULL,
    "VideoTitle" VARCHAR(255)   NOT NULL,
    "Likes" int   NOT NULL,
    "ChannelID" VARCHAR(50)   NOT NULL,
    "ChannelName" VARCHAR(50)   NOT NULL,
    "ChannelHandle" VARCHAR(50)   NOT NULL,
    "Subscribers" int   NOT NULL,
    "ThumbnailUrl" VARCHAR(50)   NOT NULL,
    "Captions" TEXT   NOT NULL,
    "Duration" int   NOT NULL,
    "GenderCount" int   NOT NULL,
    "Lighting" int   NOT NULL,
    "Audio" int   NOT NULL,
    CONSTRAINT "pk_YoutubeVideo" PRIMARY KEY (
        "VideoID"
     )
);

CREATE TABLE "ExerciseNameAlias" (
    "ExerciseNameAliasID" SERIAL   NOT NULL,
    "ExerciseID" int   NOT NULL,
    "ExerciseNameAlias" VARCHAR(50)   NOT NULL,
    CONSTRAINT "pk_ExerciseNameAlias" PRIMARY KEY (
        "ExerciseNameAliasID"
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

ALTER TABLE "ExerciseNameAlias" ADD CONSTRAINT "fk_ExerciseNameAlias_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseDescription" ADD CONSTRAINT "fk_ExerciseDescription_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseBodyArea" ADD CONSTRAINT "fk_ExerciseBodyArea_ExerciseID" FOREIGN KEY("ExerciseID")
REFERENCES "Exercises" ("ExerciseID");

ALTER TABLE "ExerciseBodyArea" ADD CONSTRAINT "fk_ExerciseBodyArea_BodyAreaID" FOREIGN KEY("BodyAreaID")
REFERENCES "BodyArea" ("BodyAreaID");

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

CREATE INDEX "idx_Exercises_ExerciseName"
ON "Exercises" ("ExerciseName");

CREATE INDEX "idx_Equipment_EquipmentName"
ON "Equipment" ("EquipmentName");

CREATE INDEX "idx_BodyPlane_BodyPlane"
ON "BodyPlane" ("BodyPlane");

CREATE INDEX "idx_BodyArea_BodyArea"
ON "BodyArea" ("BodyArea");

CREATE INDEX "idx_ExerciseNameAlias_ExerciseNameAlias"
ON "ExerciseNameAlias" ("ExerciseNameAlias");

