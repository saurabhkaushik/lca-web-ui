

class Highlight_Service:
    def __init__(self) -> None:
        pass
    
    def highlight_text(self, content, hl_index): 
        processed_text = ""
        last_index = 0
        len_text = len(content)
        for key in hl_index: 
            start_index = hl_index[key]["start_index"] 
            end_index = hl_index[key]["end_index"]
            flag = hl_index[key]["relevence_degree"]      
            score = hl_index[key]['score']  
            label = hl_index[key]['label']
            if flag == "HIGH": 
                processed_text += content[last_index:start_index] + "<div class=\"hover-text\"><mark style=\"color: white; background-color: red;\">" + content[start_index:end_index] + "<span class=\"tooltip-text\">Label : \'" + label + "\'; Score : " + str(int(score)) + "%</span></mark></div>" 
            elif flag == "MEDIUM": 
                processed_text += content[last_index:start_index] + "<div class=\"hover-text\"><mark style=\"color: white; background-color: yellow;\">" + content[start_index:end_index] + "<span class=\"tooltip-text\">Label : \'" + label + "\'; Score : " + str(int(score)) + "%</span></mark></div>" 
            elif flag == "LOW": 
                processed_text += content[last_index:start_index] + "<div class=\"hover-text\"><mark style=\"color: white; background-color: green;\">" + content[start_index:end_index] + "<span class=\"tooltip-text\">Label : \'" + label + "\'; Score : " + str(int(score)) + "% </span></mark></div>" 
            last_index = end_index
        if last_index != len_text:
            processed_text += content[last_index:len_text]
        return processed_text