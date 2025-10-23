import os
import requests
from flask import Flask, request, Response

app = Flask(__name__)

# --- LLM API Configuration ---
API_KEY = "AIzaSyBBTu7LmZkXPGweEsBtr02AVuNgdslzDfQ"
LLM_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

# --- Helper Functions (unchanged) ---
def calculate_metrics(original_text, corrected_text):
    original_words = original_text.split()
    corrected_words = corrected_text.split()

    total_original_words = len(original_words)
    total_corrected_words = len(corrected_words)

    errors = 0
    correct_words = 0
    for i in range(min(total_original_words, total_corrected_words)):
        if original_words[i] != corrected_words[i]:
            errors += 1
        else:
            correct_words += 1
    errors += abs(total_original_words - total_corrected_words)

    accuracy_rate = 0.0
    if total_original_words > 0:
        accuracy_rate = ((total_original_words - errors) / total_original_words) * 100

    missing_data_per_count_time = abs(total_original_words - total_corrected_words)
    needs_suggestions = 1 if errors > 0 else 0
    auto_assistant_becomes_0 = 1 if needs_suggestions == 1 else 0

    return {
        "errors": errors,
        "accuracy_rate": f"{accuracy_rate:.2f}%",
        "correct_words": correct_words,
        "missing_data_per_count_time": missing_data_per_count_time,
        "needs_suggestions": needs_suggestions,
        "auto_assistant_becomes_0": auto_assistant_becomes_0,
    }

def call_llm(prompt_text):
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt_text}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 1000
        }
    }
    try:
        response = requests.post(LLM_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        if result and result.get('candidates') and result['candidates'][0].get('content') and result['candidates'][0]['content'].get('parts'):
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return "Error: Could not get a valid response from the AI."
    except requests.exceptions.RequestException as e:
        return f"Error: Could not connect to AI. ({e})"
    except Exception as e:
        return f"Error: An internal error occurred. ({e})"

def generate_html(
    input_word_correction="", output_word_correction="", metrics_word_correction=None,
    input_sentence_correction="", output_sentence_correction="", metrics_sentence_correction=None,
    input_command_correction="", output_command_correction="", metrics_command_correction=None,
    input_space_correction="", output_space_correction="", metrics_space_correction=None,
    active_card=None
):
    default_metrics = {
        "errors": "-", "accuracy_rate": "-", "correct_words": "-",
        "missing_data_per_count_time": "-", "needs_suggestions": "-", "auto_assistant_becomes_0": "-"
    }
    metrics_word_correction = metrics_word_correction or default_metrics
    metrics_sentence_correction = metrics_sentence_correction or default_metrics
    metrics_command_correction = metrics_command_correction or default_metrics
    metrics_space_correction = metrics_space_correction or default_metrics

    # Determine if we're showing a specific card or all cards
    show_all_cards = active_card is None
    
    # Helper functions for clean single card view
    def get_single_card_title():
        if active_card == "word": return "Word Correction"
        elif active_card == "sentence": return "Sentence Correction"
        elif active_card == "command": return "Command Correction"
        elif active_card == "space": return "Spacing Correction"
    
    def get_single_card_placeholder():
        if active_card == "word": return "misspelled words"
        elif active_card == "sentence": return "sentence"
        elif active_card == "command": return "wrong command"
        elif active_card == "space": return "spacing issues"
    
    def get_single_card_button():
        if active_card == "word": return "Correct Words"
        elif active_card == "sentence": return "Correct Sentences"
        elif active_card == "command": return "Correct Command"
        elif active_card == "space": return "Fix Spacing"
    
    def get_single_card_input():
        if active_card == "word": return input_word_correction
        elif active_card == "sentence": return input_sentence_correction
        elif active_card == "command": return input_command_correction
        elif active_card == "space": return input_space_correction
    
    def get_single_card_output():
        if active_card == "word": return output_word_correction
        elif active_card == "sentence": return output_sentence_correction
        elif active_card == "command": return output_command_correction
        elif active_card == "space": return output_space_correction
    
    def get_single_card_metrics():
        if active_card == "word": return metrics_word_correction
        elif active_card == "sentence": return metrics_sentence_correction
        elif active_card == "command": return metrics_command_correction
        elif active_card == "space": return metrics_space_correction
    
    def has_output():
        return bool(get_single_card_output())
    
    def get_action():
        return f"{active_card}_correction"

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>✦ Virtual Typing Assistant Pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', sans-serif;
            background: #ffffff;
            min-height: 100vh;
        }}
        .glass-card {{
            background: #ffffff;
            border: 2px solid #e5e7eb;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            height: 100%; /* SAME HEIGHT */
        }}
        .glass-card:hover {{
            border-color: #000000;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        }}
        .title-text {{
            background: linear-gradient(135deg, #000000 0%, #333333 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .btn-premium {{
            background: linear-gradient(135deg, #000000 0%, #333333 100%);
            transition: all 0.3s ease;
        }}
        .btn-premium:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        }}
        .input-field {{
            background: #f9fafb;
            border: 2px solid #e5e7eb;
            transition: all 0.3s ease;
        }}
        .input-field:focus {{
            border-color: #000000;
            box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.1);
            background: #ffffff;
        }}
        .result-box {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #000000 0%, #333333 100%);
            color: white;
            transition: all 0.3s ease;
        }}
        .metric-card:hover {{ transform: scale(1.05); }}
        .back-btn {{
            background: linear-gradient(135deg, #ef4444, #dc2626);
        }}
        .card-icon {{
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #000000 0%, #333333 100%);
            color: white;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }}
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .fade-in-up {{ animation: fadeInUp 0.6s ease forwards; }}
        .card-hover {{ transition: all 0.3s ease; }}
        .card-hover:hover {{ transform: translateY(-8px); }}
        .grid-container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }}
        @media (max-width: 768px) {{ .grid-container {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body class="bg-white">
    <div class="max-w-6xl mx-auto px-4 py-8">
        {'''<div class="text-center mb-12 fade-in-up">
            <h1 class="text-5xl md:text-7xl font-bold title-text mb-4">✦ Virtual Typing Assistant Pro</h1>
            <p class="text-2xl text-gray-600 font-medium">AI-Powered Precision Correction</p>
        </div>''' if show_all_cards else ''}
        
        {'''
        <!-- ALL CARDS VIEW - PERFECT 2x2 GRID - SAME SIZE -->
        <div class="grid-container mb-8">
            <!-- TOP ROW: Card 1 & Card 2 -->
            <!-- Card 1: Word Correction -->
            <div class="glass-card p-8 rounded-3xl card-hover fade-in-up" style="animation-delay: 0.1s;">
                <form method="POST" action="/">
                    <input type="hidden" name="action" value="word_correction">
                    <input type="hidden" name="active_card" value="word">
                    <div class="flex items-center mb-6">
                        <div class="card-icon mr-4"><i class="fas fa-font"></i></div>
                        <h2 class="text-2xl font-bold text-black">Word Correction</h2>
                    </div>
                    <textarea name="input_text" rows="3" placeholder="e.g., mispelled wrods..." 
                        class="input-field w-full p-4 rounded-2xl text-lg resize-none font-mono mb-4"></textarea>
                    <button type="submit" class="btn-premium w-full py-4 rounded-2xl text-white font-semibold text-lg">
                        <i class="fas fa-spell-check mr-2"></i>Correct Words
                    </button>
                </form>
            </div>

            <!-- Card 2: Sentence Correction -->
            <div class="glass-card p-8 rounded-3xl card-hover fade-in-up" style="animation-delay: 0.2s;">
                <form method="POST" action="/">
                    <input type="hidden" name="action" value="sentence_correction">
                    <input type="hidden" name="active_card" value="sentence">
                    <div class="flex items-center mb-6">
                        <div class="card-icon mr-4"><i class="fas fa-align-left"></i></div>
                        <h2 class="text-2xl font-bold text-black">Sentence Correction</h2>
                    </div>
                    <textarea name="input_text" rows="3" placeholder="e.g., this is a gramatticaly..." 
                        class="input-field w-full p-4 rounded-2xl text-lg resize-none font-mono mb-4"></textarea>
                    <button type="submit" class="btn-premium w-full py-4 rounded-2xl text-white font-semibold text-lg">
                        <i class="fas fa-edit mr-2"></i>Correct Sentences
                    </button>
                </form>
            </div>

            <!-- BOTTOM ROW: Card 3 & Card 4 -->
            <!-- Card 3: Command Correction -->
            <div class="glass-card p-8 rounded-3xl card-hover fade-in-up" style="animation-delay: 0.3s;">
                <form method="POST" action="/">
                    <input type="hidden" name="action" value="command_correction">
                    <input type="hidden" name="active_card" value="command">
                    <div class="flex items-center mb-6">
                        <div class="card-icon mr-4"><i class="fas fa-terminal"></i></div>
                        <h2 class="text-2xl font-bold text-black">Command Correction</h2>
                    </div>
                    <textarea name="input_text" rows="3" placeholder="e.g., open da fiile on dekstop" 
                        class="input-field w-full p-4 rounded-2xl text-lg resize-none font-mono mb-4"></textarea>
                    <button type="submit" class="btn-premium w-full py-4 rounded-2xl text-white font-semibold text-lg">
                        <i class="fas fa-play mr-2"></i>Correct Command
                    </button>
                </form>
            </div>

            <!-- Card 4: Spacing Correction -->
            <div class="glass-card p-8 rounded-3xl card-hover fade-in-up" style="animation-delay: 0.4s;">
                <form method="POST" action="/">
                    <input type="hidden" name="action" value="space_correction">
                    <input type="hidden" name="active_card" value="space">
                    <div class="flex items-center mb-6">
                        <div class="card-icon mr-4"><i class="fas fa-text-width"></i></div>
                        <h2 class="text-2xl font-bold text-black">Spacing Correction</h2>
                    </div>
                    <textarea name="input_text" rows="3" placeholder="e.g., Thisisbadlyspacedtext..." 
                        class="input-field w-full p-4 rounded-2xl text-lg resize-none font-mono mb-4"></textarea>
                    <button type="submit" class="btn-premium w-full py-4 rounded-2xl text-white font-semibold text-lg">
                        <i class="fas fa-align-justify mr-2"></i>Fix Spacing
                    </button>
                </form>
            </div>
        </div>
        ''' if show_all_cards else f'''
        <!-- SINGLE CARD VIEW -->
        <div class="fade-in-up">
            <!-- Back Button -->
            <form method="POST" action="/" class="mb-8">
                <input type="hidden" name="active_card" value="">
                <button type="submit" class="back-btn text-white px-8 py-4 rounded-2xl font-semibold flex items-center mx-auto text-lg">
                    <i class="fas fa-arrow-left mr-2"></i>Back to Dashboard
                </button>
            </form>
            
            <!-- Active Card Details -->
            <div class="glass-card p-12 rounded-3xl max-w-4xl mx-auto">
                <div class="text-center mb-8">
                    <div class="card-icon mx-auto mb-4 w-20 h-20"><i class="{"fas fa-font" if active_card=='word' else "fas fa-align-left" if active_card=='sentence' else "fas fa-terminal" if active_card=='command' else "fas fa-text-width"}"></i></div>
                    <h2 class="text-4xl font-bold text-black mb-2">{get_single_card_title()}</h2>
                    <p class="text-gray-600 text-lg">AI-Powered Precision Correction</p>
                </div>
                
                <form method="POST" action="/">
                    <input type="hidden" name="action" value="{get_action()}">
                    <input type="hidden" name="active_card" value="{active_card}">
                    <div class="mb-8">
                        <label class="block text-black font-semibold mb-4 text-xl">Enter text to correct:</label>
                        <textarea name="input_text" rows="5" 
                            class="input-field w-full p-5 rounded-3xl text-xl resize-none font-mono" 
                            placeholder="Type your {get_single_card_placeholder()} here...">
                            {get_single_card_input()}
                        </textarea>
                    </div>
                    <button type="submit" class="btn-premium w-full py-5 rounded-3xl text-white font-semibold text-2xl">
                        <i class="{"fas fa-spell-check" if active_card=='word' else "fas fa-edit" if active_card=='sentence' else "fas fa-play" if active_card=='command' else "fas fa-align-justify"} mr-3"></i>
                        {get_single_card_button()}
                    </button>
                </form>

                {f'''
                <div class="mt-12">
                    <h3 class="text-3xl font-semibold text-black mb-8 text-center"> Corrected Result</h3>
                    <div class="result-box p-8 rounded-3xl font-mono text-xl min-h-[120px] mb-8 border-l-4 border-black">
                        <div class="text-black text-2xl">{get_single_card_output()}</div>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                        <div class="metric-card p-8 rounded-3xl text-center">
                            <div class="text-4xl font-bold">{get_single_card_metrics()['errors']}</div>
                            <div class="text-base opacity-90 mt-2">Errors</div>
                        </div>
                        <div class="metric-card p-8 rounded-3xl text-center bg-gradient-to-r from-green-600 to-green-800">
                            <div class="text-4xl font-bold">{get_single_card_metrics()['accuracy_rate']}</div>
                            <div class="text-base opacity-90 mt-2">Accuracy</div>
                        </div>
                        <div class="metric-card p-8 rounded-3xl text-center bg-gradient-to-r from-blue-600 to-purple-700">
                            <div class="text-4xl font-bold">{get_single_card_metrics()['correct_words']}</div>
                            <div class="text-base opacity-90 mt-2">Correct</div>
                        </div>
                    </div>
                </div>
                ''' if has_output() else ''}
            </div>
        </div>
        '''}
    </div>

    <footer class="mt-16 text-center py-12 border-t border-gray-200">
        <p class="text-gray-600 font-medium">✦ Virtual Typing Assistant Pro 2024 | All Rights Reserved</p>
    </footer>

    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            document.querySelectorAll('.card-hover').forEach(function(card, index) {{
                card.style.animationDelay = (index * 0.1) + 's';
            }});
        }});
    </script>
</body>
</html>
    """
    return html_content

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')
        active_card = request.form.get('active_card', '')
        input_text = request.form.get('input_text', '')
        
        if active_card == '':  # Back to cards
            return Response(generate_html(active_card=None), mimetype='text/html')
        
        # Process correction for active card
        prompt_prefix = ""
        if action == "word_correction":
            prompt_prefix = "Correct the spelling of these words: "
        elif action == "sentence_correction":
            prompt_prefix = "Correct the grammar and spelling of this sentence: "
        elif action == "command_correction":
            prompt_prefix = "Interpret and correct this natural language command. Output only the corrected command: "
        elif action == "space_correction":
            prompt_prefix = "Correct the spacing in this text. Output only the text with corrected spacing: "
        
        corrected_output = call_llm(f"{prompt_prefix}{input_text}")
        metrics = calculate_metrics(input_text, corrected_output)

        # Return appropriate response based on active card
        if active_card == "word":
            return Response(generate_html(
                input_word_correction=input_text,
                output_word_correction=corrected_output,
                metrics_word_correction=metrics,
                active_card="word"
            ), mimetype='text/html')
        elif active_card == "sentence":
            return Response(generate_html(
                input_sentence_correction=input_text,
                output_sentence_correction=corrected_output,
                metrics_sentence_correction=metrics,
                active_card="sentence"
            ), mimetype='text/html')
        elif active_card == "command":
            return Response(generate_html(
                input_command_correction=input_text,
                output_command_correction=corrected_output,
                metrics_command_correction=metrics,
                active_card="command"
            ), mimetype='text/html')
        elif active_card == "space":
            return Response(generate_html(
                input_space_correction=input_text,
                output_space_correction=corrected_output,
                metrics_space_correction=metrics,
                active_card="space"
            ), mimetype='text/html')
        
    return Response(generate_html(active_card=None), mimetype='text/html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))