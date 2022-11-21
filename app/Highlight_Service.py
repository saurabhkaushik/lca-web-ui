

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
        score_context_sent = 0
        score_context_total = 0
        score_context_high = 0
        score_context_medium = 0
        score_context_low = 0
        count_presence_json = {'TotalCount' : 0}
        for key in hl_index:
            start_index = hl_index[key]["start_index"]
            end_index = hl_index[key]["end_index"]            
            p_score = int(hl_index[key]['p_score'])
            s_score = int(hl_index[key]['s_score'])
            c_score = int(hl_index[key]['c_score'])
            sc_score = int((s_score + c_score) / 2)
            flag = self.get_flag(sc_score) 
            label = hl_index[key]['label']            
            if p_score > 70:
                score_context_sent += sc_score
                score_context_total += 100
                if label in count_presence_json.keys()  : 
                    count_presence_json[label] += 1
                else: 
                    count_presence_json[label] = 0
                count_presence_json[label] += 1
                count_presence_json['TotalCount'] += 1
                if flag == "HIGH":
                    processed_text += content[last_index:start_index] + "<div class=\"hover-text\"><mark style=\"color: white; background-color: red;\">" + content[start_index:end_index] + \
                        "<span class=\"tooltip-text\">Label : \'" + label.lower() + "\'; Risk : " + flag + \
                        " P_Score : " + str(p_score) + "%; S_Score : " + \
                        str(sc_score) + "%</span></mark></div>"
                    score_context_high += sc_score
                elif flag == "MEDIUM":
                    processed_text += content[last_index:start_index] + "<div class=\"hover-text\"><mark style=\"color: white; background-color: orange;\">" + content[start_index:end_index] + \
                        "<span class=\"tooltip-text\">Label : \'" + label.lower() + "\'; Risk : " + flag + \
                        " P_Score : " + str(p_score) + "%; S_Score : " + \
                        str(sc_score) + "%</span></mark></div>"
                    score_context_medium += sc_score
                elif flag == "LOW":
                    processed_text += content[last_index:start_index] + "<div class=\"hover-text\"><mark style=\"color: white; background-color: green;\">" + content[start_index:end_index] + \
                        "<span class=\"tooltip-text\">Label : \'" + label.lower() + "\'; Risk : " + flag + \
                        " P_Score : " + str(p_score) + "%; S_Score : " + \
                        str(sc_score) + "% </span></mark></div>"
                    score_context_low += sc_score
            else: 
                processed_text += content[last_index:start_index] + "<div class=\"hover-text\"><mark style=\"color: black; background-color: white;\">" + content[start_index:end_index] + \
                        "<span class=\"tooltip-text\">Label : \'" + label.lower() + "\'; Risk : " + flag + \
                        " P_Score : " + str(p_score) + "%; S_Score : " + \
                        str(sc_score) + "%</span></mark></div>"
            last_index = end_index
        if last_index != len_text:
            processed_text += content[last_index:len_text]

        if score_context_total != 0:
            score_context_sent = (score_context_sent / score_context_total) * 100
            score_context_high = (score_context_high / score_context_total) * 100
            score_context_medium = (score_context_medium / score_context_total) * 100
            score_context_low = (score_context_low / score_context_total) * 100
        score_context_json = {'ScoreContext': score_context_sent, 'ScoreContextHigh' : score_context_high, 'ScoreContextMedium' : score_context_medium, 'ScoreContextLow' : score_context_low}
        return processed_text, score_context_json, count_presence_json
