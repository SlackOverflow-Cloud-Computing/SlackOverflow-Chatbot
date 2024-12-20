from openai import OpenAI
from app.models.traits import Traits
from app.models.chat_details import ChatDetails
from typing import Optional
import json
import logging
from fastapi import HTTPException

logger = logging.getLogger("uvicorn")


# with the help of ChatGPT:
SYS_PROMPT_RECOMMENDATION = """
You are a system that processes user descriptions of songs and generates a JSON response with the following attributes. Based on the user's input, populate the values for minimum (`min_`), maximum (`max_`), or target (`target_`) for each attribute. If the user does not describe an aspect of the song, leave the corresponding value as `null`.

### Attributes to Populate:

1. `min_acousticness`, `max_acousticness`, `target_acousticness`  
   Type: number  
   - For each tunable track attribute, a hard floor (`min_`) or hard ceiling (`max_`) can be provided.  
   - Example: `min_acousticness=0.5` filters for tracks that are at least 50% acoustic.  
   - The `target_` value specifies the preferred level of acousticness.  
   - Range: 0 - 1  

2. `min_danceability`, `max_danceability`, `target_danceability`  
   Type: number  
   - Specifies the danceability of the song, from low to high.  
   - Example: `target_danceability=0.8` prioritizes highly danceable tracks.  
   - Range: 0 - 1  

3. `min_duration_ms`, `max_duration_ms`, `target_duration_ms`  
   Type: integer  
   - Duration of the song in milliseconds.  
   - Example: `max_duration_ms=240000` restricts results to songs under 4 minutes.  

4. `min_energy`, `max_energy`, `target_energy`  
   Type: number  
   - Measures the intensity and activity of the song.  
   - Example: `target_energy=0.7` prefers moderately high-energy tracks.  
   - Range: 0 - 1  

5. `min_instrumentalness`, `max_instrumentalness`, `target_instrumentalness`  
   Type: number  
   - Indicates whether the track is primarily instrumental.  
   - Example: `min_instrumentalness=0.5` filters for tracks that are mostly instrumental.  
   - Range: 0 - 1  

6. `min_key`, `max_key`, `target_key`  
   Type: integer  
   - Specifies the musical key of the song.  
   - Range: 0 - 11  

7. `min_liveness`, `max_liveness`, `target_liveness`  
   Type: number  
   - Reflects the presence of an audience in the recording.  
   - Example: `target_liveness=0.3` prefers studio recordings over live performances.  
   - Range: 0 - 1  

8. `min_loudness`, `max_loudness`, `target_loudness`  
   Type: number  
   - Specifies the overall loudness of the track in decibels.  

9. `min_mode`, `max_mode`, `target_mode`  
   Type: integer  
   - Indicates whether the track is in a major (`1`) or minor (`0`) mode.  
   - Range: 0 - 1  

10. `min_popularity`, `max_popularity`, `target_popularity`  
    Type: integer  
    - Defines the popularity of the track, scored from 0 (least popular) to 100 (most popular).  

11. `min_speechiness`, `max_speechiness`, `target_speechiness`  
    Type: number  
    - Reflects the presence of spoken words in the track.  
    - Example: `min_speechiness=0.4` filters for tracks that are mostly spoken word.  
    - Range: 0 - 1  

12. `min_tempo`, `max_tempo`, `target_tempo`  
    Type: number  
    - Specifies the tempo of the track in beats per minute (BPM).  
    - Example: `min_tempo=120` filters for faster tracks suitable for workouts.  

13. `min_time_signature`, `max_time_signature`, `target_time_signature`  
    Type: integer  
    - Defines the time signature of the track (e.g., 4/4).  
    - Maximum Value: 11  

14. `min_valence`, `max_valence`, `target_valence`  
    Type: number  
    - Measures the positivity or happiness of the track.  
    - Example: `target_valence=0.9` prioritizes tracks with a happy mood.  
    - Range: 0 - 1  

### Behavior:
1. Interpretation: Interpret the user's song description and map it to the relevant attributes.
2. Default Values: If a specific attribute is not described by the user, leave its value as `null`.
3. Response Format: Generate the following JSON structure with inferred values based on the description.

### Example:

**User Input:**  
"A high-energy, fast-paced dance track with little vocals, great for a workout."

**Generated JSON Response:**  
```json
{
  "min_acousticness": null,
  "max_acousticness": 0.2,
  "target_acousticness": null,
  "min_danceability": 0.7,
  "max_danceability": null,
  "target_danceability": 0.9,
  "min_duration_ms": null,
  "max_duration_ms": null,
  "target_duration_ms": null,
  "min_energy": 0.8,
  "max_energy": null,
  "target_energy": 0.9,
  "min_instrumentalness": 0.5,
  "max_instrumentalness": null,
  "target_instrumentalness": null,
  "min_key": null,
  "max_key": null,
  "target_key": null,
  "min_liveness": null,
  "max_liveness": null,
  "target_liveness": null,
  "min_loudness": null,
  "max_loudness": null,
  "target_loudness": null,
  "min_mode": null,
  "max_mode": null,
  "target_mode": null,
  "min_popularity": null,
  "max_popularity": null,
  "target_popularity": null,
  "min_speechiness": 0.1,
  "max_speechiness": null,
  "target_speechiness": null,
  "min_tempo": 120,
  "max_tempo": null,
  "target_tempo": 140,
  "min_time_signature": null,
  "max_time_signature": null,
  "target_time_signature": null,
  "min_valence": 0.7,
  "max_valence": null,
  "target_valence": 0.9
}"""

SYS_PROMPT_PREFERENCE = """
You are a Music Preference Analyzer assistant. Your task is to analyze the user's chat history, which includes timestamps and conversation content, to understand the user's music preferences. Pay special attention to how the user's preferences may have evolved over time. Based on your analysis, provide insightful observations about the user's musical tastes and recommend relevant songs that align with these preferences.

# Instructions

1. **Analyze Chat History**:
   - Review each entry in the user's chat history, noting the date, time, and content of each message.
   - Identify the types of music requests made (e.g., random songs, holiday-specific music, mood-based songs).
   - Detect any patterns or shifts in the user's music preferences over time.

2. **Identify Music Preferences**:
   - Determine preferred genres, artists, moods, and specific themes based on the user's requests.
   - Note any recurring requests or specific criteria mentioned by the user.

3. **Detect Temporal Trends**:
   - Observe how the user's preferences change with time or specific events (e.g., seasonal requests like Thanksgiving music).
   - Identify any increasing or decreasing interest in certain music styles or themes.

4. **Provide Insights**:
   - Summarize the key findings from the analysis.
   - Explain possible reasons behind the user's music preferences and their changes over time.

5. **Recommend Songs**:
   - Based on the analysis, suggest a list of songs that align with the user's identified preferences.
   - Ensure recommendations are diverse yet cohesive, reflecting both consistent and evolving tastes.

# Output Format

- **Analysis Summary**:
  Provide a detailed summary of the user's music preferences, highlighting key genres, artists, moods, and any observed changes over time.

- **Insights**:
  Share insightful observations about the user's musical tastes, including possible reasons for their preferences and how they have evolved.

- **Recommended Songs**:
  List 10 recommended songs that align with the user's preferences. Format each recommendation as follows:
  - **Song Title** by **Artist Name** - [Genre/Mood Descriptor]

# Example

**Input Chat History**:

"""

SYS_PROMPT_CHAT = """ 
You are a knowledgeable and engaging Music Expert assistant. 
Your role is to interact with users in a conversational manner about music-related topics. Each interaction includes the user's chat history with timestamps and the new input message. 
Based on this information, you should analyze the user's music preferences, identify any changes or trends over time, and determine whether the user is requesting song recommendations.
Do NOT provide actual song recommendations to the user. If they request recommendations, simply tell them that you have provided your recommendations.

### Instructions:

1. **Analyze Chat History and New Input:**
   - Review the user's chat history, noting the dates, times, and content of each message.
   - Understand the context and identify any patterns or shifts in the user's music preferences.

2. **Determine if Recommendations are Needed:**
   - If the user's new input indicates a desire for song recommendations, then set "need_recommendation" to True, and then:
      - If the recommendation is not enough, ask for more recommendation requirements.
   - Otherwise, set it to False.

3. **Generate Content:**
   - Provide an appropriate response based on the user's input.
   - If recommendations are needed, inform the user that recommendations will be provided.
   - If not, respond accordingly without mentioning recommendations.

4. **Format the Output:**
   - Ensure the response is a dictionary with the keys "content" and "need_recommendation" as shown in the example.

### Example Input:

### User Chat History ###
human: hi, tell me some fun facts about the music world today.
ai: Sure! Here is some content...

### User New Input ###
I want to have some happy song


### Example JSON Output:
{
"content": "Sure! I will provide you with some recommendations.", 
"need_recommendation": True
}


### Additional Notes:

- Maintain a friendly and engaging tone.
- Keep responses clear and concise.
- When recommending songs, ensure they align with the user's identified preferences.
- Handle various user inputs gracefully, determining when recommendations are appropriate.
- If they have asked for music, ensure that need_recommendation is set to True! It also HAS to be set to true if you say you are providing recommendations.
"""

TRAITS = [
    "min_acousticness",
    "max_acousticness",
    "target_acousticness",
    "min_danceability",
    "max_danceability",
    "target_danceability",
    "min_duration_ms",
    "max_duration_ms",
    "target_duration_ms",
    "min_energy",
    "max_energy",
    "target_energy",
    "min_instrumentalness",
    "max_instrumentalness",
    "target_instrumentalness",
    "min_key",
    "max_key",
    "target_key",
    "min_liveness",
    "max_liveness",
    "target_liveness",
    "min_loudness",
    "max_loudness",
    "target_loudness",
    "min_mode",
    "max_mode",
    "target_mode",
    "min_popularity",
    "max_popularity",
    "target_popularity",
    "min_speechiness",
    "max_speechiness",
    "target_speechiness",
    "min_tempo",
    "max_tempo",
    "target_tempo",
    "min_time_signature",
    "max_time_signature",
    "target_time_signature",
    "min_valence",
    "max_valence",
    "target_valence"
]

genres = ["acoustic", "afrobeat", "alt-rock", "alternative", "ambient", "anime", "black-metal", "bluegrass", "blues", "bossanova", "brazil", "breakbeat", "british", "cantopop", "chicago-house", "children", "chill", "classical", "club", "comedy", "country", "dance", "dancehall", "death-metal", "deep-house", "detroit-techno", "disco", "disney", "drum-and-bass", "dub", "dubstep", "edm", "electro", "electronic", "emo", "folk", "forro", "french", "funk", "garage", "german", "gospel", "goth", "grindcore", "groove", "grunge", "guitar", "happy", "hard-rock", "hardcore", "hardstyle", "heavy-metal", "hip-hop", "holidays", "honky-tonk", "house", "idm", "indian", "indie", "indie-pop", "industrial", "iranian", "j-dance", "j-idol", "j-pop", "j-rock", "jazz", "k-pop", "kids", "latin", "latino", "malay", "mandopop", "metal", "metal-misc", "metalcore", "minimal-techno", "movies", "mpb", "new-age", "new-release", "opera", "pagode", "party", "philippines-opm", "piano", "pop", "pop-film", "post-dubstep", "power-pop", "progressive-house", "psych-rock", "punk", "punk-rock", "r-n-b", "rainy-day", "reggae", "reggaeton", "road-trip", "rock", "rock-n-roll", "rockabilly", "romance", "sad", "salsa", "samba", "sertanejo", "show-tunes", "singer-songwriter", "ska", "sleep", "songwriter", "soul", "soundtracks", "spanish", "study", "summer", "swedish", "synth-pop", "tango", "techno", "trance", "trip-hop", "turkish", "work-out", "world-music"]

class OpenAIService:
    
    def __init__(self, token, org=None):
        self.client = OpenAI(api_key=token, organization=org)
    
    # https://platform.openai.com/docs/quickstart?language-preference=python
    def extract_song_traits(self, query: str, cid: str) -> Optional[Traits]:
        """Given a query, extract a songs traits and genres and return the JSON representation"""
        logger.info(f"Getting song traits from query: {query} - [{cid}]")
        for _ in range(3): # Try 3 times
            traits_completion = self._chat(query, SYS_PROMPT_RECOMMENDATION, cid)
            genre_completion = self._chat(
                query,
                f"Given the description from the user, write out the genres that apply from the following list:\n{genres}",
                cid
            )
            output_json = self._verify_traits_json(traits_completion, cid)
            if output_json is None:
                continue
            output_json = self._extract_genres(genre_completion, output_json, cid)
            if output_json is None:
                continue
            logger.info(f"Got song traits: {output_json} - [{cid}]")
            return output_json
        logger.error(f"Failed to get song traits: {query} - [{cid}]")
        raise HTTPException(status_code=500, detail="Failed get song traits")

    def analyze_user_preference(self, chat_history: list[ChatDetails], cid: str) -> str:
        """Analyze the user preference with given chat history, return agent message"""
        query = "**User's Chat History:**"
        logger.info(f"Analyzing user preference. Chat history: {chat_history} - [{cid}]")
        for chat in chat_history:
            query += f"\n{str(chat.created_at)} - {chat.content}"

        preference_completion = self._chat(
            query,
            SYS_PROMPT_PREFERENCE,
            cid
        )
        logger.info(f"Got user preferences: {preference_completion} - [{cid}]")
        return preference_completion

    def general_chat(self, query: str, chat_history: list[ChatDetails], cid: str) -> dict:
        """
        Generate the multiple rounds chat with user, return with a json in the format of
        {
            "content":"...",
            "need_recommendation": True
        }
        """
        logger.info(f"Generating standard chat response for: {query} - [{cid}]")
        formatted_history = "### User Chat History ###"
        for chat in chat_history:
            formatted_history += f"\n{chat.role}: {chat.content}"

        formatted_input = formatted_history + f"\n\n### User New Input ###\n{query}"

        try:
            chat_completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYS_PROMPT_CHAT},
                    {
                        "role": "user",
                        "content": formatted_input
                    }
                ],
                response_format={
                    "type": "json_object"
                },
            )
        except Exception as e:
            logger.error(f"OpenAI failure: {e} - [{cid}]")
            raise HTTPException(status_code=500, detail=str(e))
        
        chat_response = chat_completion.choices[0].message.content
        chat_response = json.loads(chat_response)
        logger.info(f"Got chat response: {chat_response} - [{cid}]")
        return chat_response


    def _chat(self, query: str, sys_prompt: str, cid: str, model="gpt-4o-mini"):
        """Send a request to GPT"""
        try:
            completion = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {
                            "role": "user",
                            "content": query
                        }
                    ]
            )
        except Exception as e:
            logger.error(f"OpenAI failure: {e} - [{cid}]")
            return None
        return completion.choices[0].message.content

    def _verify_traits_json(self, output: str, cid: str):
        """Verify the JSON provided from GPT and add missing fields"""
        logger.info(f"Verifying json: {output} - [{cid}]")
        try:
            start = output.index("{")
            end = output.index("}")
            output_json = json.loads(output[start:end+1])
        except Exception as e:
            logger.error(f"JSON decode error: {output} - [{cid}]")
            return None
        for trait in TRAITS:
            if trait not in output_json:
                logger.error(f"Missing trait: {trait} - [{cid}]")
                return None
        for key in output_json:
            if key not in TRAITS:
                logger.error(f"Extra key: {key} - [{cid}]")
                return None
            
        output_json["limit"] = 3
        output_json["market"] = "US"
        
        return output_json

    def _extract_genres(self, output: str, curr_json, cid: str):
        """Extract genres from GPT response"""
        logger.info(f"Extracting genres: {output} - [{cid}]")
        curr_json["genres"] = []
        for genre in genres:
            if genre in output:
                curr_json["genres"].append(genre)
        if len(curr_json["genres"]) == 0:
            logger.error(f"No genres found: {output} - [{cid}]")
            return None
        return curr_json