import gradio as gr
import json
import re
import html
import os
import pandas as pd
from models import senti_pipeline, classifier
# # # # # from database import init_db, save_review, get_dynamic_reviews

# Initialize database
# init_db()
# json_path = "Yelp3k.json"

# # Load static reviews
# Open the JSON file and load its contents
with open('yelp3k.json', 'r', encoding='utf-8') as fp:
    static_reviews = json.load(fp)
def highlight_aspects(text, aspects):
    aspects_sorted = sorted(aspects, key=len, reverse=True)
    aspects_regex = [re.escape(asp) for asp in aspects_sorted]
    pattern = r'\b(?:' + '|'.join(aspects_regex) + r')\b'
    def replace_match(match):
        return f'<span style="font-weight: bold; background-color: yellow;">{match.group()}</span>'
    return re.sub(pattern, replace_match, text, flags=re.IGNORECASE)

# Format a single review
def format_review(review):
    text = review['text']
    aspects = review.get('aspects', []) or review.get('aspect_word', '').split(',')
    emotions = review.get('emotions', []) or review.get('emotion', '').split(',')
    highlighted_text = highlight_aspects(text, aspects)
    # aspects_html = "<ul>" + "".join(f"<li>{html.escape(asp)}</li>" for asp in aspects) + "</ul>"
    # emotions_html = "<ul>" + "".join(f"<li>{emo}</li>" for emo in emotions) + "</ul>"
    
    aspects = [asp.strip() for asp in review['aspect_word'].split(',')]
    emotions = [emo.strip() for emo in review['emotion'].split(',')]
    aspects_html = '<div class="cell-grid">' + "".join(f'<div class="cell-item">{html.escape(asp)}</div>' for asp in aspects) + '</div>'
    emotions_html = '<div class="cell-grid">' + "".join(f'<div class="cell-item">{html.escape(emo)}</div>' for emo in emotions) + '</div>'
    stars = review.get('stars', 'N/A')
    return f"""
    <div style="border: 1px solid #ccc; padding: 10px; margin-bottom: 10px;">
        <h4>Review</h4>
        <p>{highlighted_text}</p>
        <p>Stars: {stars}</p>
        <h3>Aspect Words</h3>
        {aspects_html}
        <h3>Emotions</h3>
        {emotions_html}
    </div>
    """

# Format dynamic reviews
def format_dynamic_reviews(reviews):
    return "<div>" + "".join(format_review(rev) for rev in reviews) + "</div>"

# Get static review
def get_static_review(index):
    review = static_reviews[index]
    highlighted_text = highlight_aspects(review['text'], review['aspect_word'].split(','))
    stars_html = f"Stars: {review['stars']}"
    # aspects_html = '<h3>Aspect Words</h3><div class="aspect-grid">' + "".join(f'<div class="aspect-item">{html.escape(asp)}</div>' for asp in review['aspect_word'].split(',')) + '</div>'
    # emotions_html = "<ul>" + "".join(f"<li>{emo}</li>" for emo in review['emotion'].split(',')) + "</ul>"
    aspects = [asp.strip() for asp in review['aspect_word'].split(',')]
    emotions = [emo.strip() for emo in review['emotion'].split(',')]

    aspects_html = '<div class="cell-grid">' + "".join(f'<div class="cell-item">{html.escape(asp)}</div>' for asp in aspects) + '</div>'
    emotions_html = '<div class="cell-grid">' + "".join(f'<div class="cell-item">{html.escape(emo)}</div>' for emo in emotions) + '</div>'
    
    info_text = f"Review {index+1} of {len(static_reviews)}"
    return highlighted_text, stars_html, aspects_html, emotions_html, info_text

# Navigation
def navigate(direction, current_index):
    if direction == 'prev':
        return max(current_index - 1, 0)
    return min(current_index + 1, len(static_reviews) - 1)

# Submit new review
def submit_new_review(text):
    if not text.strip():
        return "Please enter a review.", []
    aspects_result = senti_pipeline(text)
    aspects = [ent['word'] for ent in aspects_result if ent['entity_group'] == 'ASPECT']
    emotion_result = classifier(text)
    emotions = [emo['label'] for emo in emotion_result if emo['score'] > 0.3]
    # # save_review(text, aspects, emotions)
    # # new_dynamic_reviews = get_dynamic_reviews()
    new_dynamic_reviews= "hello db heroku"
    return format_dynamic_reviews(new_dynamic_reviews), new_dynamic_reviews

# Gradio interface
with gr.Blocks(css="""
.cell-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 10px;
}
.cell-item {
    background-color: #f0f0f0;
    padding: 10px;
    border: 1px solid #ccc;
    text-align: center;
}
""") as demo:
    # Header
    gr.Markdown("# Yelp Review Demonstration for Aspect and Emotion Extracted")

    # Static Reviews
    with gr.Row():
        with gr.Column(scale=11):
            static_text = gr.HTML(label="Review Text")
        with gr.Column(scale=1):
            static_stars = gr.HTML(label="Stars")
    static_aspects = gr.HTML(label=None)
    static_emotions = gr.HTML(label="Emotions")
    static_info = gr.Textbox(label="Review Info", interactive=False)
    with gr.Row():
        prev_button = gr.Button("Previous")
        next_button = gr.Button("Next")

    # Submit Form
    gr.Markdown("## Submit Your Review")
    with gr.Row():
        with gr.Column(scale=8):
            submit_text = gr.Textbox(label="Write your review", lines=5)
            submit_button = gr.Button("Submit")

    # Dynamic Reviews
    gr.Markdown("## User Submitted Reviews")
    dynamic_display = gr.HTML()

    # States
    current_static_index = gr.State(0)
    dynamic_reviews_state = gr.State()

    # Load Initial Data
    demo.load(get_static_review, inputs=current_static_index, outputs=[static_text, static_stars, static_aspects, static_emotions, static_info])
    # # demo.load(lambda: (format_dynamic_reviews(get_dynamic_reviews()), get_dynamic_reviews()), inputs=None, outputs=[dynamic_display, dynamic_reviews_state])

    # Event Handlers
    prev_button.click(lambda ci: navigate('prev', ci), inputs=current_static_index, outputs=current_static_index).then(
        get_static_review, inputs=current_static_index, outputs=[static_text, static_stars, static_aspects, static_emotions, static_info])
    next_button.click(lambda ci: navigate('next', ci), inputs=current_static_index, outputs=current_static_index).then(
        get_static_review, inputs=current_static_index, outputs=[static_text, static_stars, static_aspects, static_emotions, static_info])
    submit_button.click(submit_new_review, inputs=submit_text, outputs=[dynamic_display, dynamic_reviews_state])

# Launch
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 7850))
    demo.launch(server_name="0.0.0.0", server_port=port,share=True)