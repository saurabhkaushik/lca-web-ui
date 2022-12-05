
present_base_score = 90 # keyword_threshold

class Highlight_Service:
    def __init__(self) -> None:
        pass

    def get_flag(self, score):
        #score = int (((score - present_base_score) / (100 - present_base_score)) * 100)
        flag = ''
        if score < 30:
            flag = "LOW"
        else:
            if score >= 30 and score <= 70:
                flag = "MEDIUM"
            else:
                if score > 70:
                    flag = "HIGH"
        return flag

    def highlight_text(self, hl_index):
        processed_text = ""

        score_presence_count_total = 0
        score_context_high_count = 0
        score_context_medium_count = 0
        score_context_low_count = 0
        score_risk_sents = 0

        score_presence_count_json = {}
        for key in hl_index:
            c_sentence = hl_index[key]['sentence']
            label = hl_index[key]['label']   

            p_score = int(hl_index[key]['presence_score'])
            c_score = int(hl_index[key]['context_score'])
            risk_score = int(hl_index[key]['risk_score'])               
                      
            if p_score > present_base_score:
                score_risk_sents += risk_score
                score_presence_count_total += 1
                if label in score_presence_count_json.keys(): 
                    score_presence_count_json[label] += 1
                else: 
                    score_presence_count_json[label] = 1

                flag = self.get_flag(c_score) 

                if flag == "HIGH":
                    processed_text += "<div class=\"hover-text\"><mark style=\"color: white; background-color: crimson;\">" + c_sentence + \
                        "<span class=\"tooltip-text\">Label : \'" + label.lower() + "\'; Risk : " + flag.capitalize() + \
                        "; Presence Score : " + str(p_score) + "%; Context Score : " + \
                        str(c_score) + "%; Risk Score : " + str(risk_score) + "%</span></mark></div>"
                    score_context_high_count += 1
                elif flag == "MEDIUM":
                    processed_text += "<div class=\"hover-text\"><mark style=\"color: white; background-color: darkorange;\">" + c_sentence + \
                        "<span class=\"tooltip-text\">Label : \'" + label.lower() + "\'; Risk : " + flag.capitalize() + \
                        "; Presence Score : " + str(p_score) + "%; Context Score : " + \
                        str(c_score) + "%; Risk Score : " + str(risk_score) + "%</span></mark></div>"
                    score_context_medium_count += 1
                elif flag == "LOW":
                    processed_text += "<div class=\"hover-text\"><mark style=\"color: black; background-color: gold;\">" + c_sentence + \
                        "<span class=\"tooltip-text\">Label : \'" + label.lower() + "\'; Risk : " + flag.capitalize() + \
                        "; Presence Score : " + str(p_score) + "%; Context Score : " + \
                        str(c_score) + "%; Risk Score : " + str(risk_score) + "% </span></mark></div>"
                    score_context_low_count += 1
            else: 
                flag = self.get_flag(c_score) 
                processed_text += "<div class=\"hover-text\"><mark style=\"color: black; background-color: white;\">" + c_sentence + \
                        "<span class=\"tooltip-text\">Label : \'" + label.lower() + "\'; Risk : " + flag.capitalize() + \
                        "; Presence Score : " + str(p_score) + "%; Context Score : " + \
                        str(c_score) + "%; Risk Score : " + str(risk_score) + "%</span></mark></div>"

        # Context Scoring 
        score_report_risk_score = 0
        if score_presence_count_total != 0:
            score_report_risk_score = (score_risk_sents / score_presence_count_total)

        # Context Strength Percentage based on Score 
        score_report_json = {'score_report_risk_score': int(score_report_risk_score)}
        # Context Count Percentage based on Counts  
        score_context_count_json = {'score_context_high_count' : int(score_context_high_count), 'score_context_medium_count' : int(score_context_medium_count), 'score_context_low_count' : int(score_context_low_count)}
        
        label_keys = list(score_presence_count_json.keys())
        label_values = list(score_presence_count_json.values())
        score_presence_count_json['label_keys'] = label_keys
        score_presence_count_json['label_values'] = label_values

        print ('score_report_json:', score_report_json)
        print ('score_context_count_json:', score_context_count_json)
        print ('score_presence_count_json:', score_presence_count_json)
        return processed_text, score_report_json, score_context_count_json, score_presence_count_json
