from flask import Flask, render_template, request, jsonify
import os
import whisper


# ========================================
# FFmpeg PATH
# ========================================

FFMPEG_PATH = r"C:\Users\KIIT0001\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin"

os.environ["PATH"] += os.pathsep + FFMPEG_PATH


# ========================================
# FLASK APP
# ========================================

app = Flask(__name__)


# ========================================
# LOAD WHISPER
# ========================================

print("Loading Whisper model...")

model = whisper.load_model("base")

print("Whisper model loaded successfully!")


# ========================================
# HOME PAGE
# ========================================

@app.route("/")
def home():
    return render_template("index.html")


# ========================================
# INTERVIEW PAGE
# ========================================

@app.route("/interview")
def interview():
    return render_template("interview.html")


# ========================================
# AUDIO UPLOAD
# ========================================

@app.route("/upload", methods=["POST"])
def upload():

    print("\n================================")
    print("AUDIO UPLOAD RECEIVED")
    print("================================")

    # ----------------------------------------
    # CHECK FILE
    # ----------------------------------------

    if "audio" not in request.files:

        print("ERROR: No audio file received")

        return jsonify({
            "success": False,
            "message": "No audio file received"
        }), 400


    audio_file = request.files["audio"]

    print("Audio filename:", audio_file.filename)


    # ----------------------------------------
    # CREATE UPLOAD FOLDER
    # ----------------------------------------

    upload_folder = "uploads"

    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)


    # ----------------------------------------
    # SAVE AUDIO
    # ----------------------------------------

    audio_path = os.path.join(
        upload_folder,
        "interview.webm"
    )

    audio_file.save(audio_path)

    print("Audio saved at:", audio_path)


    # ----------------------------------------
    # CHECK FILE SIZE
    # ----------------------------------------

    file_size = os.path.getsize(audio_path)

    print("Audio file size:", file_size, "bytes")


    if file_size < 1000:

        print("ERROR: Audio file is too small")

        return jsonify({
            "success": False,
            "message": "Audio recording is empty or incomplete."
        }), 400


    # ========================================
    # WHISPER TRANSCRIPTION
    # ========================================

    try:

        print("\nStarting Whisper transcription...")


        result = model.transcribe(
            audio_path,
            fp16=False
        )


        transcription = result["text"].strip()


        print("\n================================")
        print("TRANSCRIPTION:")
        print(transcription)
        print("================================")


        # ========================================
        # INTERVIEW QUESTION
        # ========================================

        question = "Tell me about yourself."


        # ========================================
        # RELEVANCE ANALYSIS
        # ========================================

        answer_lower = transcription.lower()


        relevance_categories = {

            "personal": [
                "name",
                "myself",
                "student",
                "from",
                "belong"
            ],

            "education": [
                "student",
                "college",
                "university",
                "school",
                "degree",
                "engineering",
                "computer science",
                "cse",
                "btech",
                "study",
                "studying",
                "education"
            ],

            "skills": [
                "skill",
                "skills",
                "python",
                "java",
                "c++",
                "programming",
                "coding",
                "software",
                "developer",
                "development"
            ],

            "technology": [
                "ai",
                "artificial intelligence",
                "machine learning",
                "ml",
                "data science",
                "technology",
                "technologies",
                "web",
                "database",
                "cloud"
            ],

            "experience": [
                "project",
                "projects",
                "internship",
                "experience",
                "work",
                "worked",
                "training",
                "certification"
            ],

            "career": [
                "career",
                "future",
                "goal",
                "goals",
                "interested",
                "interest",
                "aspire",
                "aspiring"
            ]
        }


        # ========================================
        # FIND MATCHING CATEGORIES
        # ========================================

        matched_categories = []
        matched_keywords = []


        for category, words in relevance_categories.items():

            category_found = False

            for word in words:

                if word in answer_lower:

                    matched_keywords.append(word)

                    category_found = True


            if category_found:

                matched_categories.append(category)


        # ----------------------------------------
        # REMOVE DUPLICATES
        # ----------------------------------------

        matched_keywords = list(
            dict.fromkeys(matched_keywords)
        )


        # ========================================
        # CATEGORY SCORE
        # ========================================

        category_score = (
            len(matched_categories)
            /
            len(relevance_categories)
        ) * 100


        # ========================================
        # ANSWER LENGTH SCORE
        # ========================================

        word_count = len(
            transcription.split()
        )


        if word_count < 3:

            length_score = 10

        elif word_count < 8:

            length_score = 30

        elif word_count < 15:

            length_score = 60

        elif word_count < 30:

            length_score = 80

        else:

            length_score = 100


        # ========================================
        # FINAL RELEVANCE SCORE
        # ========================================

        relevance_score = int(
            (category_score * 0.75)
            +
            (length_score * 0.25)
        )


        relevance_score = max(
            0,
            min(
                100,
                relevance_score
            )
        )


        # ========================================
        # FILLER WORD DETECTION
        # ========================================

        filler_words = [

            "um",
            "uh",
            "hmm",
            "like",
            "actually",
            "basically",
            "literally",
            "you know",
            "i mean",
            "sort of",
            "kind of"

        ]


        filler_counts = {}


        for filler in filler_words:

            count = answer_lower.count(filler)

            if count > 0:

                filler_counts[filler] = count


        total_fillers = sum(
            filler_counts.values()
        )


        # ========================================
        # PRINT ANALYSIS
        # ========================================

        print("\n================================")
        print("RELEVANCE ANALYSIS")
        print("================================")

        print(
            "Matched categories:",
            matched_categories
        )

        print(
            "Matched keywords:",
            matched_keywords
        )

        print(
            "Word count:",
            word_count
        )

        print(
            "Relevance Score:",
            relevance_score
        )


        print("\n================================")
        print("FILLER WORD ANALYSIS")
        print("================================")

        print(
            "Total filler words:",
            total_fillers
        )

        print(
            "Detected fillers:",
            filler_counts
        )


        # ========================================
        # RETURN RESULT
        # ========================================

        return jsonify({

            "success": True,

            "message":
                "Audio analyzed successfully",

            "transcription":
                transcription,

            "question":
                question,

            "relevance_score":
                relevance_score,

            "matched_keywords":
                matched_keywords,

            "filler_count":
                total_fillers,

            "filler_words":
                filler_counts

        })


    # ========================================
    # ERROR HANDLING
    # ========================================

    except Exception as error:

        print("\n================================")
        print("TRANSCRIPTION ERROR:")
        print("================================")

        print(error)


        return jsonify({

            "success": False,

            "message":
                "Transcription failed",

            "error":
                str(error)

        }), 500


# ========================================
# RUN APPLICATION
# ========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )