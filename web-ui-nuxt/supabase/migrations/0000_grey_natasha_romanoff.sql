CREATE TABLE IF NOT EXISTS "exercise_sentences" (
	"exercise_id" uuid NOT NULL,
	"sentence_id" uuid NOT NULL,
	CONSTRAINT "exercise_sentences_pk" PRIMARY KEY("exercise_id","sentence_id")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "exercises" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"title" text NOT NULL,
	"description" text NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "sentences" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"content" text NOT NULL,
	"ipa_transcription" text,
	"arpabet_transcription" text,
	"word_count" integer NOT NULL,
	"char_count_no_spaces" integer NOT NULL,
	"char_count_total" integer NOT NULL,
	"difficulty_level" integer NOT NULL,
	"translation_ru" text
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "user_exercise_sentence_progress" (
	"user_id" uuid NOT NULL,
	"exercise_id" uuid NOT NULL,
	"sentence_id" uuid NOT NULL,
	"status" text DEFAULT 'not attempted' NOT NULL,
	CONSTRAINT "user_exercise_sentence_progress_pk" PRIMARY KEY("user_id","exercise_id","sentence_id")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "user_profiles" (
	"user_id" uuid PRIMARY KEY NOT NULL,
	"avatar_path" text,
	"completed_exercises_count" integer DEFAULT 0 NOT NULL,
	"sentences_by_difficulty" jsonb DEFAULT '{}' NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "user_progress" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" uuid NOT NULL,
	"exercise_id" uuid NOT NULL,
	"completion_status" text DEFAULT 'not started' NOT NULL,
	"last_attempted" timestamp DEFAULT now() NOT NULL,
	"rating" integer,
	CONSTRAINT "rating_check" CHECK ("user_progress"."completion_status" = 'done' AND "user_progress"."rating" IS NOT NULL OR "user_progress"."completion_status" != 'done' AND "user_progress"."rating" IS NULL)
);
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "exercise_sentences" ADD CONSTRAINT "exercise_sentences_exercise_id_exercises_id_fk" FOREIGN KEY ("exercise_id") REFERENCES "public"."exercises"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "exercise_sentences" ADD CONSTRAINT "exercise_sentences_sentence_id_sentences_id_fk" FOREIGN KEY ("sentence_id") REFERENCES "public"."sentences"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "user_exercise_sentence_progress" ADD CONSTRAINT "user_exercise_sentence_progress_exercise_id_exercises_id_fk" FOREIGN KEY ("exercise_id") REFERENCES "public"."exercises"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "user_exercise_sentence_progress" ADD CONSTRAINT "user_exercise_sentence_progress_sentence_id_sentences_id_fk" FOREIGN KEY ("sentence_id") REFERENCES "public"."sentences"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "user_progress" ADD CONSTRAINT "user_progress_exercise_id_exercises_id_fk" FOREIGN KEY ("exercise_id") REFERENCES "public"."exercises"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
