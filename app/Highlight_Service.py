
class Highlight_Service:
    def __init__(self) -> None:
        pass

    def get_flag(self, score):
        #score = int (((score - present_base_score) / (100 - present_base_score)) * 100)
        flag = ''
        if score < 40:
            flag = "LOW"
        else:
            if score >= 40 and score <= 80:
                flag = "MEDIUM"
            else:
                if score > 80:
                    flag = "HIGH"
        return flag

    def highlight_text(self, hl_index, present_base_score):
        processed_text = ""

        score_presence_count_total = 0
        score_context_high_count = 0
        score_context_medium_count = 0
        score_context_low_count = 0
        score_risk_sents = 0
        class_analysis = {}

        score_presence_count_json = {}
        for key in hl_index:
            c_sentence = hl_index[key]['sentence']
            label = hl_index[key]['label']   

            p_score = int(hl_index[key]['presence_score'])
            c_score = int(hl_index[key]['context_score'])
            risk_score = int(hl_index[key]['risk_score'])               
                      
            if p_score >= present_base_score:
                score_risk_sents += risk_score
                score_presence_count_total += 1
                if label in score_presence_count_json.keys(): 
                    score_presence_count_json[label] += 1
                else: 
                    score_presence_count_json[label] = 1

                if not label in class_analysis.keys():
                    class_analysis[label]= {'count': 0, 'score': 0}
                else: 
                    class_analysis[label]['count'] += 1 
                    class_analysis[label]['score'] += c_score
                
                flag = self.get_flag(c_score) 

                if flag == "HIGH":
                    processed_text += "<div class=\"hover-text\"><mark style=\"color: white; background-color: crimson;\"><span onclick=\"submitFORM('/training_new', 'POST', {'label' : '" + label.lower() + "', 'content': this.textContent})\">" + c_sentence + \
                        "</span><span class=\"tooltip-text\">Label : \'" + label.lower() + "\'; Risk : " + flag.capitalize() + \
                        "; Presence Score : " + str(p_score) + "%; Context Score : " + \
                        str(c_score) + "%; Risk Score : " + str(risk_score) + "%</span></mark></div>"
                    score_context_high_count += 1
                elif flag == "MEDIUM":
                    processed_text += "<div class=\"hover-text\"><mark style=\"color: white; background-color: darkorange;\"><span onclick=\"submitFORM('/training_new', 'POST', {'label' : '" + label.lower() + "', 'content': this.textContent})\">" + c_sentence + \
                        "</span><span class=\"tooltip-text\">Label : \'" + label.lower() + "\'; Risk : " + flag.capitalize() + \
                        "; Presence Score : " + str(p_score) + "%; Context Score : " + \
                        str(c_score) + "%; Risk Score : " + str(risk_score) + "%</span></mark></div>"
                    score_context_medium_count += 1
                elif flag == "LOW":
                    processed_text += "<div class=\"hover-text\"><mark style=\"color: black; background-color: gold;\"><span onclick=\"submitFORM('/training_new', 'POST', {'label' : '" + label.lower() + "', 'content': this.textContent})\">" + c_sentence + \
                        "</span><span class=\"tooltip-text\">Label : \'" + label.lower() + "\'; Risk : " + flag.capitalize() + \
                        "; Presence Score : " + str(p_score) + "%; Context Score : " + \
                        str(c_score) + "%; Risk Score : " + str(risk_score) + "% </span></mark></div>"
                    score_context_low_count += 1
            else: 
                flag = self.get_flag(c_score) 
                processed_text += "<div class=\"hover-text\"><mark style=\"color: black; background-color: white;\"><span onclick=\"submitFORM('/training_new', 'POST', {'label' : '" + label.lower() + "', 'content': this.textContent})\">" + c_sentence + \
                        "</span><span class=\"tooltip-text\">Label : \'" + label.lower() + "\'; Risk : " + flag.capitalize() + \
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

        class_obj = {}
        for data in class_analysis: 
            if class_analysis[data]['count'] == 0:
                class_analysis[data]['avg'] = 0
            else: 
                class_analysis[data]['avg'] = class_analysis[data]['score'] / class_analysis[data]['count']
            class_obj[data] = class_analysis[data]['avg']

        print('Label Class Strength:', class_obj)
        print ('score_report_json:', score_report_json)
        print ('score_context_count_json:', score_context_count_json)
        print ('score_presence_count_json:', score_presence_count_json)
        return processed_text, score_report_json, score_context_count_json, score_presence_count_json, class_obj
