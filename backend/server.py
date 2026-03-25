from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

@app.route('/api/convert', methods=['POST'])
def convert():
    try:
        data = request.json
        mode = data.get('mode')
        input_text = data.get('text', '')
        language = data.get('language', 'english')

        # --- MODE 1: USR -> JSON ---
        if mode == "USR-JSON":
            try:
                from json_formatter import JsonFormatter
                # Initialize without paths to avoid creating dummy folders
                formatter = JsonFormatter() 
                result = formatter.process_string(input_text)
                return jsonify({'output': result})
            except Exception as e:
                return jsonify({'error': f'JsonFormatter Error: {str(e)}'}), 500

        # --- MODE 2: JSON -> NLG ---
        elif mode == "JSON-NLG":
            try:
                import sanskrit_nlg
                # Pass the raw string and language directly to the script
                result = sanskrit_nlg.process_text(input_text, language)
                return jsonify({'output': result})
            except Exception as e:
                return jsonify({'error': f'NLG Error: {str(e)}'}), 500

        # --- MODE 3: USR -> NLG ---
        elif mode == "USR-NLG":
            try:
                import sanskrit_usr_paragraph_nlg_inference as usr_nlg
                result = usr_nlg.process_text(input_text, language, "gemini-2.5-flash")
                return jsonify({'output': result})
            except Exception as e:
                return jsonify({'output': f'USR-NLG Error: {str(e)}'}), 200  # Return output for blank fix

        else:
            return jsonify({'error': 'Unknown mode'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Sanskrit Converter API Server (In-Memory Version) Running on port 5000")
    app.run(debug=True, port=5000)