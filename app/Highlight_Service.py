

class Highlight_Service:
    def __init__(self) -> None:
        pass

    def get_flag(self, score):
        flag = ''
        if score > 30:
            flag = "LOW"
        else:
            if score >= -30 and score <= 30:
                flag = "MEDIUM"
            else:
                if score < -30:
                    flag = "HIGH"
        return flag

    def highlight_text(self, content, hl_index):
        processed_text = ""
        last_index = 0
        len_text = len(content)
        score_context_total = 0
        score_context_sents = 0
        score_context_high = 0
        score_context_medium = 0
        score_context_low = 0
        score_context_high_count = 0
        score_context_medium_count = 0
        score_context_low_count = 0
        score_context_total_count = 0
        score_presence_json = {}
        lable_count = 0
        for key in hl_index:
            label = hl_index[key]['label']  
            start_index = hl_index[key]["start_index"]
            end_index = hl_index[key]["end_index"]            
            p_score = int(hl_index[key]['p_score'])
            s_score = int(hl_index[key]['s_score'])
            c_score = int(hl_index[key]['c_score'])
            sc_score = int((s_score + c_score) / 2)
            flag = self.get_flag(sc_score) 
                      
            if p_score > 75:
                score_context_sents += sc_score
                score_context_total += 100
                score_context_total_count += 1
                if label in score_presence_json.keys(): 
                    score_presence_json[label] += 1
                else: 
                    score_presence_json[label] = 1
                    lable_count += 1
                #score_presence_json['TotalCount'] += 1

                if flag == "HIGH":
                    processed_text += content[last_index:start_index] + "<div class=\"hover-text\"><mark style=\"color: black; background-color: LightSalmon;\">" + content[start_index:end_index] + \
                        "<span class=\"tooltip-text\">Label : \'" + label.lower() + "\'; Risk : " + flag.capitalize() + \
                        "; Presence Score : " + str(p_score) + "%; Context Score : " + \
                        str(sc_score) + "%</span></mark></div>"
                    score_context_high += sc_score
                    score_context_high_count += 1
                elif flag == "MEDIUM":
                    processed_text += content[last_index:start_index] + "<div class=\"hover-text\"><mark style=\"color: black; background-color: orange;\">" + content[start_index:end_index] + \
                        "<span class=\"tooltip-text\">Label : \'" + label.lower() + "\'; Risk : " + flag.capitalize() + \
                        "; Presence Score : " + str(p_score) + "%; Context Score : " + \
                        str(sc_score) + "%</span></mark></div>"
                    score_context_medium += sc_score
                    score_context_medium_count += 1
                elif flag == "LOW":
                    processed_text += content[last_index:start_index] + "<div class=\"hover-text\"><mark style=\"color: black; background-color: lightgreen;\">" + content[start_index:end_index] + \
                        "<span class=\"tooltip-text\">Label : \'" + label.lower() + "\'; Risk : " + flag.capitalize() + \
                        "; Presence Score : " + str(p_score) + "%; Context Score : " + \
                        str(sc_score) + "% </span></mark></div>"
                    score_context_low += sc_score
                    score_context_low_count += 1
            else: 
                processed_text += content[last_index:start_index] + "<div class=\"hover-text\"><mark style=\"color: black; background-color: white;\">" + content[start_index:end_index] + \
                        "<span class=\"tooltip-text\">Label : \'" + label.lower() + "\'; Risk : " + flag.capitalize() + \
                        "; Presence Score : " + str(p_score) + "%; Context Score : " + \
                        str(sc_score) + "%</span></mark></div>"
            last_index = end_index

        if last_index != len_text:
            processed_text += content[last_index:len_text]

        # Context Scoring 
        if score_context_total != 0:
            score_context_sents = (score_context_sents / score_context_total) * 100
            score_context_high = (score_context_high / score_context_total) * 100
            score_context_medium = (score_context_medium / score_context_total) * 100
            score_context_low = (score_context_low / score_context_total) * 100
            #score_context_high_count = (score_context_high_count / score_context_total_count) * 100
            #score_context_medium_count = (score_context_medium_count / score_context_total_count) * 100
            #score_context_low_count = (score_context_low_count / score_context_total_count) * 100

        # Context Strength Percentage based on Score 
        score_context_json = {'ScoreContextTotal': int(score_context_sents), 'ScoreContextHigh' : int(score_context_high), 'ScoreContextMedium' : int(score_context_medium), 'ScoreContextLow' : int(score_context_low)}
        # Context Count Percentage based on Counts  
        score_context_count_json = {'score_context_total_count': int(score_context_total_count), 'score_context_high_count' : int(score_context_high_count), 'score_context_medium_count' : int(score_context_medium_count), 'score_context_low_count' : int(score_context_low_count)}
        #score_presence_json['lable_count'] = lable_count
        label_keys = list(score_presence_json.keys())
        label_values = list(score_presence_json.values())
        score_presence_json['label_keys'] = label_keys
        score_presence_json['label_values'] = label_values
        print ('score_context_json:', score_context_json)
        print ('score_context_count_json:', score_context_count_json)
        print ('score_presence_json:', score_presence_json)
        return processed_text, score_context_json, score_context_count_json, score_presence_json
