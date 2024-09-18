from typing import List

from langchain.schema import HumanMessage

from gpt_model_manger import GPTModelManager


class PromptService:

    @staticmethod
    def extract_goz_number_from_string(insurance_text: str) -> tuple[str, str]:
        gpt_manager = GPTModelManager()

        prompt = f"""  
        Du musst eine GOZ Nummer aus einer Textantwort einer Krankenkasse extrahieren, auf die sich in dem Text hauptsächlich bezogen wird.
        
        Regeln: 
        - Extrahiere nur die GOZ Nummer und gebe entsprechend nur die Nummer zurück. 
        - Wenn du eine GOZ Nummer gefunden hast, darf unter keinen Umständen in deiner Antwort etwas anderes als die Nummer stehen.
        - Wenn du keine Nummer extrahieren kannst, antworte nur mit XXX_NOTHING_FOUND_XXX
                
        Text der Krankenkasse:
        {insurance_text}
        """
        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content

    @staticmethod
    def evaluate_no_tariff_benefit_hard(insurance_text: str) -> tuple[str, bool]:
        gpt_manager = GPTModelManager()

        prompt = f"""  
            Überprüfe, ob der folgende Text einer Krankenkasse der Aussage "Für diese Aufwendungen sieht der Tarif keine Leistungen vor." entspricht. Die Übereinstimmung der beiden Texte muss im Wortlaut fast Deckungsgleich sein. Nur sinngemäße Texte stimmen nicht überein.
            
            Regeln: 
            - Antworte ausschließlich mit true oder false. Es darf nichts anderes als ein Boolean zurück gegeben werden.

            Text der Krankenkasse:
            {insurance_text}
            """
        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content.lower() == "true"

    @staticmethod
    def evaluate_no_tariff_benefit_soft(insurance_text: str) -> tuple[str, bool]:
        gpt_manager = GPTModelManager()

        prompt = f"""  
            Überprüfe, ob der folgende Text einer Krankenkasse beanstandet, dass eine Leistung nicht im Tarif abgedeckt wird.
            
            Regeln: 
            - Es darf nur mit true geantwortet werden, wenn die Krankenkasse wortgemäß oder sinngemäß beanstandet, dass die Leistung nicht vom Tarif des Kunden abgedeckt wird
            - Es muss hierbei nicht explizit von der Krankenkasse erwähnt werden, jedoch zumindest sinngemäß
            - Antworte ausschließlich mit true oder false. Es darf nichts anderes als ein Boolean zurück gegeben werden.

            Text der Krankenkasse:
            {insurance_text}
            """
        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content.lower() == "true"

    @staticmethod
    def write_tariff_benefit_text() -> tuple[str, str]:
        gpt_manager = GPTModelManager()

        no_tariff_benefit_sample = """
        Leider müssen wir Ihnen mitteilen, dass die beanstandeten Leistungen nicht von Ihrem Versicherungstarif abgedeckt sind. Bei dem abgeschlossenen Tarif handelt es sich um eine selektive Deckung, die spezifisch festlegt, welche zahnärztlichen Behandlungen erstattet werden und welche nicht. Die Leistungen, die im Rahmen Ihrer Behandlung in Anspruch genommen wurden, fallen nicht unter die in Ihrem Tarif inkludierten Leistungen.
        Wir verstehen, dass dies möglicherweise enttäuschend für Sie ist, jedoch basieren die Entscheidungen der PKV streng auf den Bedingungen Ihres gewählten Tarifs. Wir empfehlen Ihnen, die genauen Details und Einschränkungen Ihres Tarifs direkt mit Ihrer Versicherung zu klären, um zukünftige Missverständnisse zu vermeiden.
        """

        prompt = f"""  
        Du erhältst einen Mustertext "no_tariff_benefit_sample", welcher eine Beispiel Antwort an einen Patienten ist, dessen Tarif die Leistung nicht abdeckt
        Regeln: 
        - Die Muster Text Sektion ist mit XXX_NO_TARIFF_BENEFIT_TEXT_START_XXX und XXX_NO_TARIFF_BENEFIT_TEXT_END_XXX gekennzeichnet. 
        - Schreibe einen Text der sich an NO_TARIFF_BENEFIT orientiert, der Informationsgehalt darf hierbei nicht verändert werden.
        - Der Text benötigt keine Anrede oder ähnliches da dieser später noch zu einem vollständigen Text zusammen gesetzt wird.
        - Du darfst in keinem Fall die Markierungen wie z.B "XXX_NO_TARIFF_BENEFIT_TEXT_START_XXX" der Sektion mit in die Antwort schreiben
        
        XXX_NO_TARIFF_BENEFIT_TEXT_START_XXX
        {no_tariff_benefit_sample}
        XXX_NO_TARIFF_BENEFIT_TEXT_END_XXX
        """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content

    @staticmethod
    def evaluate_muster_title_for_message(insurance_text: str, sample_title: str) -> tuple[str, bool]:
        gpt_manager = GPTModelManager()

        prompt = f"""  
        Du bekommst eine Nachricht einer Krankenkasse in der ein Teil einer Rechnung beanstandet wird. Prüfe ob der Mustertitel die beanstandung relativiert kann.
        
        Regeln: 
        - Die Nachricht der Krankenkasse ist mit XXX_INSURANCE_TEXT_START_XXX und XXX_INSURANCE_TEXT_END_XXX gekennzeichnet. 
        - Der Mustertitel ist mit XXX_SAMPLE_TITLE_START_XXX und XXX_SAMPLE_TITLE_END_XXX gekennzeichnet. 
        - Antworte außschließlich mit true oder false. Es darf nichts anderes als ein Boolean zurück gegeben werden.
        - Eine Argumentation im Mustertitel muss nicht zwingend die Beanstandung vollständig negieren, um als Relativierung zu gelten. Es reicht, wenn plausible alternative Sichtweisen oder zusätzliche Kontexte angeboten werden, die die absolute Gültigkeit der Beanstandung mindern könnten.
        - Wenn der Mustertitel spezifische Aspekte der Beanstandung anspricht oder erklärt, warum die Beanstandung unter bestimmten Umständen nicht zutreffend sein könnte (z.B. durch das Anführen von medizinischen oder juristischen Fachmeinungen), sollte das Ergebnis true sein.
        - Wenn der Mustertitel keine relevanten Informationen oder Argumente liefert, die die Beanstandung direkt adressieren oder in Frage stellen, sollte das Ergebnis false sein.
                    
                       
        XXX_INSURANCE_TEXT_START_XXX
        {insurance_text}
        XXX_INSURANCE_TEXT_END_XXX
        
        XXX_SAMPLE_TITLE_START_XXX
        {sample_title}
        XXX_SAMPLE_TITLE_END_XXX
        """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content.lower() == "true"

    @staticmethod
    def evaluate_muster_text_for_message(insurance_text: str, sample_text: str) -> tuple[str, bool]:
        gpt_manager = GPTModelManager()

        prompt = f"""  
        Du bekommst eine Nachricht einer Krankenkasse in der ein Teil einer Rechnung beanstandet wird. Prüfe ob der Mustertext die Beanstandung relativieren kann.
        
        Regeln: 
        - Die Nachricht der Krankenkasse ist mit XXX_INSURANCE_TEXT_START_XXX und XXX_INSURANCE_TEXT_END_XXX gekennzeichnet. 
        - Der Mustertext ist mit XXX_SAMPLE_TEXT_START_XXX und XXX_SAMPLE_TEXT_END_XXX gekennzeichnet. 
        - Antworte ausschließlich mit true oder false. Es darf nichts anderes als ein Boolean zurück gegeben werden.
                
        XXX_INSURANCE_TEXT_START_XXX
        {insurance_text}
        XXX_INSURANCE_TEXT_END_XXX
        
        XXX_SAMPLE_TEXT_START_XXX
        {sample_text}
        XXX_SAMPLE_TEXT_END_XXX
        """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content.lower() == "true"

    @staticmethod
    def write_response_from_sample_text(insurance_text: str, sample_text: str) -> tuple[str, str]:
        gpt_manager = GPTModelManager()

        prompt = f"""  
        Du bekommst eine Nachricht einer Krankenkasse in der ein Teil einer Rechnung beanstandet wird. Weiterhin bekommst du einen Mustertext, der die Beanstandung relativeren kann.
        
        Regeln: 
        - Die Nachricht der Krankenkasse ist mit XXX_INSURANCE_TEXT_START_XXX und XXX_INSURANCE_TEXT_END_XXX gekennzeichnet. 
        - Der Mustertext ist mit XXX_SAMPLE_TEXT_START_XXX und XXX_SAMPLE_TEXT_END_XXX gekennzeichnet. 
        - Formuliere einen kurzen Text, der die Beanstandung relativiert.
                
        XXX_INSURANCE_TEXT_START_XXX
        {insurance_text}
        XXX_INSURANCE_TEXT_END_XXX
        
        XXX_SAMPLE_TEXT_START_XXX
        {sample_text}
        XXX_SAMPLE_TEXT_END_XXX
        """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content

    @staticmethod
    def evaluate_urteils_title_for_message(insurance_text: str, judgment_title: str) -> tuple[str, bool]:
        gpt_manager = GPTModelManager()

        prompt = f"""  
        Du bekommst eine Nachricht einer Krankenkasse ein Teil einer Rechnung beanstandet wird. Prüfe ob der Urteilstitel die Beanstandung relativiert kann.
        
        Regeln: 
        - Die Nachricht der Krankenkasse ist mit XXX_INSURANCE_TEXT_START_XXX und XXX_INSURANCE_TEXT_END_XXX gekennzeichnet. 
        - Der Urteilstitel ist mit XXX_JUDGMENT_TITLE_START_XXX und XXX_JUDGMENT_TITLE_END_XXX gekennzeichnet. 
        - Antworte ausschließlich mit true oder false. Es darf nichts anderes als ein Boolean zurück gegeben werden.
                
        XXX_INSURANCE_TEXT_START_XXX
        {insurance_text}
        XXX_INSURANCE_TEXT_END_XXX
        
        XXX_JUDGMENT_TITLE_START_XXX
        {judgment_title}
        XXX_JUDGMENT_TITLE_END_XXX
        """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content.lower() == "true"

    @staticmethod
    def evaluate_judgment_text_for_message(insurance_text: str, judgment_text: str) -> tuple[str, bool]:
        gpt_manager = GPTModelManager()

        prompt = f"""  
        Du bekommst eine Nachricht einer Krankenkasse ein Teil einer Rechnung beanstandet wird. Prüfe ob der Urteilstext die Beanstandung relativieren kann.
        
        Regeln: 
        - Die Nachricht der Krankenkasse ist mit XXX_INSURANCE_TEXT_START_XXX und XXX_INSURANCE_TEXT_END_XXX gekennzeichnet. 
        - Der Urteilstitel ist mit XXX_JUDGMENT_TEXT_START_XXX und XXX_JUDGMENT_TEXT_END_XXX gekennzeichnet. 
        - Antworte ausschließlich mit true oder false. Es darf nichts anderes als ein Boolean zurück gegeben werden.
                
        XXX_INSURANCE_TEXT_START_XXX
        {insurance_text}
        XXX_INSURANCE_TEXT_END_XXX
        
        XXX_JUDGMENT_TEXT_START_XXX
        {judgment_text}
        XXX_JUDGMENT_TEXT_END_XXX
        """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content.lower() == "true"

    @staticmethod
    def write_response_from_urteils_text(insurance_text: str, judgment_text: str) -> tuple[str, str]:
        gpt_manager = GPTModelManager()

        prompt = f"""  
        Du bekommst eine Nachricht einer Krankenkasse in der ein Teil einer Rechnung beanstandet wird. Weiterhin bekommst du einen Urteilstext, der die Beanstandung relativeren kann.
        
        Regeln: 
        - Die Nachricht der Krankenkasse ist mit XXX_INSURANCE_TEXT_START_XXX und XXX_INSURANCE_TEXT_END_XXX gekennzeichnet. 
        - Der Urteilstitel ist mit XXX_JUDGMENT_TEXT_START_XXX und XXX_JUDGMENT_TEXT_END_XXX gekennzeichnet. 
        - Der Text soll falls vorhanden, das Aktenzeichen und das Datum des Urteils unbedingt beinhalten.
        - Formuliere einen kurzen Text, der die Beanstandung relativiert.
        - Der Text ist jedoch an den Patienten gerichtet und nicht an die Krankenkasse. Hier soll dem Patienten nahegelegt werden, wieso die Beanstandung der Krankenkasse relativiert werden kann.
                
        XXX_INSURANCE_TEXT_START_XXX
        {insurance_text}
        XXX_INSURANCE_TEXT_END_XXX
        
        XXX_JUDGMENT_TEXT_START_XXX
        {judgment_text}
        XXX_JUDGMENT_TEXT_END_XXX
        """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content

    @staticmethod
    def write_opening_text(insurance_text: str) -> tuple[str, str]:
        gpt_manager = GPTModelManager()

        prompt = f"""  
        Du bekommst eine Nachricht einer Krankenkasse in der ein Teil einer Rechnung beanstanded wird.
        
        Regeln: 
        - Die Nachricht der Krankenkasse ist mit XXX_INSURANCE_TEXT_START_XXX und XXX_INSURANCE_TEXT_END_XXX gekennzeichnet. 
        - Formuliere eine kurze Anrede an den Patienten, an den die Nachricht der Krankenkasse gerichtet wurde und fasse kurz zusammen, was die Krankenkasse beanstandet
        - Der Text soll an den Patienten gerichtet sein z.B "Ich beziehe mich auf die Nachricht der Krankenkasse in der die Kostenübernahme für ..... abgelehnt wird." und auf die Beanstandung verweisen
        - Der Text darf KEIN Abrede enthalten, da diese nur der Anfang eines Gesamttext ist, der später zusammengesetzt wird 
        - Erwähne jedoch, 
        - Dieser Text kann als Orientierung dienen "wir möchten Sie über die Details Ihrer zahnärztlichen Behandlung und die damit verbundene Abrechnung informieren, insbesondere im Hinblick auf die Beanstandung Ihrer Krankenversicherung."
    
            
        XXX_INSURANCE_TEXT_START_XXX
        {insurance_text}
        XXX_INSURANCE_TEXT_END_XXX
        
        """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content

    @staticmethod
    def write_closing_text() -> tuple[str, str]:
        gpt_manager = GPTModelManager()
        closing_text = "Ich hoffe, dass mit diesen Informationen der Erstattung aller erbrachten und verordnungskonform berechneten Leistungen nichts mehr im Wege steht. Sie können diese Informationen Ihrer kostenerstattenden Stelle zur Prüfung auf nachträgliche tarifliche Erstattung weiterleiten."
        prompt = f"""  
        Du bekommst einen kleinen Text der als Abschluss eines Schreibens dienst
        
        Regeln: 
        - Die Abschluss Sektion ist mit XXX_CLOSTING_TEXT_START_XXX und XXX_CLOSTING_TEXT_END_XXX gekennzeichnet. 
        - Formuliere aus den Informationen in der Abschluss Sektion eine kleine Abrede, diese ist an einen Patienten gerichtet.
        - Der Text darf KEIN Anrede enthalten, da diese nur der Anfang eines Gesamttext ist, der später zusammengesetzt wird 
        - Ergänze Mit freundlichen Grüßen am Ende
            
        XXX_CLOSTING_TEXT_START_XXX
        {closing_text}
        XXX_CLOSTING_TEXT_END_XXX
        
        """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content

    @staticmethod
    def write_sample_answer_text(insurance_text: str, sample_answers: List[str]) -> tuple[str, str]:
        gpt_manager = GPTModelManager()

        sample_answers_section = " XXX_NEXT_XXX ".join(sample_answers)

        prompt = f"""  
        Du bekommst eine Nachricht einer Krankenkasse in der ein Teil einer Rechnung beanstandet wird. Weiterhin bekommst du Mustertexte die die Beanstandung relativeren können.
        
        Regeln: 
        - Die Nachricht der Krankenkasse ist mit XXX_INSURANCE_TEXT_START_XXX und XXX_INSURANCE_TEXT_END_XXX gekennzeichnet. 
        - Der Gesamte Text muss immer explizit an den Patienten gerichtet sein, die Beanstandungen (INSURANCE_TEXT) kommen immer von der Versicherung.
        - Die Muster Text Sektion ist mit XXX_SAMPLE_ANSWERS_SECTION_START_XXX und XXX_SAMPLE_ANSWERS_SECTION_END_XXX gekennzeichnet. 
        - Die übergebenen Texte in den Sektionen sind immer mit XXX_NEXT_XXX voneinander getrennt.
        - Formuliere aus dem Text eine Antwort für den Patienten die ihm nahelegt weshalb die Beanstandung der Versicherung relativiert werden kann.
        - Nutze nur Informationen aus der Muster Text Sektion, wenn sie wirklich relevant und notwendig sind um die Nachricht der Krankenkasse zu relativieren bzw. zu entkräften.
        - Der Text benötigt keine Anrede oder ähnliches da dieser später noch zu einem vollständigen Text zusammen gesetzt wird.
            
        XXX_INSURANCE_TEXT_START_XXX
        {insurance_text}
        XXX_INSURANCE_TEXT_END_XXX
        
        XXX_SAMPLE_ANSWERS_SECTION_START_XXX
        {sample_answers_section}
        XXX_SAMPLE_ANSWERS_SECTION_END_XXX
        """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content

    @staticmethod
    def write_judgement_answer_text(insurance_text: str, judgments_answers: List[str]) -> tuple[str, str]:
        gpt_manager = GPTModelManager()

        sample_answers_section = " XXX_NEXT_XXX ".join(judgments_answers)

        prompt = f"""  
        Du bekommst eine Nachricht einer Krankenkasse in der ein Teil einer Rechnung beanstandet wird. Weiterhin bekommst du Urteile die die Beanstandung relativeren können.
        
        Regeln: 
        - Die Nachricht der Krankenkasse ist mit XXX_INSURANCE_TEXT_START_XXX und XXX_INSURANCE_TEXT_END_XXX gekennzeichnet. 
        - Der Gesamte Text muss immer explizit an den Patienten gerichtet sein, die Beanstandungen (INSURANCE_TEXT) kommen immer von der Versicherung.
        - Die Urteils Text Sektion ist mit XXX_JUDGEMENT_ANSWERS_SECTION_START_XXX und XXX_JUDGEMENT_ANSWERS_SECTION_END_XXX gekennzeichnet. 
        - Die übergebenen Texte in den Sektionen sind immer mit XXX_NEXT_XXX voneinander getrennt.
        - Formuliere aus dem Text eine Antwort für den Patienten die ihm nahelegt weshalb die Beanstandung der Versicherung relativiert werden kann.
        - Nutze nur Informationen aus der Urteils Text Sektion, wenn sie wirklich relevant und notwendig sind um die Nachricht der Krankenkasse zu relativieren bzw. zu entkräften.
        - Der Text benötigt keine Anrede oder ähnliches da dieser später noch zu einem vollständigen Text zusammen gesetzt wird.
        - Der Text soll falls vorhanden, das Aktenzeichen und das Datum des Urteils unbedingt beinhalten.  
        - Der Text darf auf keinen Fall den Patienten auffordern, eine Handlung zu tätigen, es dient rein zur Information      
        - Du darfst nicht das Konjunktiv verwenden
            
        XXX_INSURANCE_TEXT_START_XXX
        {insurance_text}
        XXX_INSURANCE_TEXT_END_XXX
        
        XXX_JUDGEMENT_ANSWERS_SECTION_START_XXX
        {sample_answers_section}
        XXX_JUDGEMENT_ANSWERS_SECTION_END_XXX
        """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content

    @staticmethod
    def extract_analog_keywords_from_string_to_json(analyze_string: str) -> tuple[str, str]:
        gpt_manager = GPTModelManager()

        prompt = f"""  
        Du erhältst einen String (Rechnungstext des Arztes), der eine analoge Berechnung einer Leistung enthält. Extrahiere mir die ausschließlich die analog berechnete Leistung. Es darf nichts weiter dazu geschrieben werden, lediglich der String.
        
        Regeln: 
        - extrahiere lediglich die analog berechnete Leistung
        - Wenn keine analogen Leistungen gefunden werden, antworte nur mit XXX_NOTHING_FOUND_XXX.
                
        Info:
        - § 6 Absatz 1 GOZ schafft die Möglichkeit, Leistungen, die nicht im Gebührenverzeichnis aufgenommen sind, entsprechend einer nach Art, Kostenund Zeitaufwand gleichwertigen Leistung des Gebührenverzeichnisses zu
        berechnen 
        - Eine analoge Rechnungsstellung besteht in der Regel aus drei Teilen. 
        - Erster Teil:  analog berechnete Leistung
        - Zweiter Teil: Bindeglied, Verweis auf § 6 Absatz 1 GOZ
        - Dritter Teil: besteht aus der zugrunde liegenden „alten Leistung“ und ihrer original Leistungsbeschreibung
        
        Rechnungstext des Arztes:
        {analyze_string}
        """
        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content

    @staticmethod
    def extract_regular_keywords_from_string_to_json(analyze_string: str) -> tuple[str, str]:
        gpt_manager = GPTModelManager()

        prompt = f"""  
        Du erhältst einen String (Beanstandung des Arztes), der Beanstandungen einer Leistung enhält. Extrahiere mir die Leistungen, welche von einer GOZ abgedeckt sind ( auch wenn die GOZ Nummer nicht explizit gegeben ist ). Es darf nichts weiter dazu geschrieben werden, lediglich der String. Gib die Leistungen in einer JSON-Liste zurück.
        
        Regeln: 
        - extrahiere lediglich die Leistungen
        - Wenn keine Leistungen gefunden werden, antworte nur mit XXX_NOTHING_FOUND_XXX.
        - Wenn Leistungen gefunden werden, darf wirklich nur die JSON Liste zurück gegeben werden als String
        - Du darfst kein GOZ Nummer extrahieren, sondern nur die Leistungen
                
        Beanstandung der Krankenkasse:
        {analyze_string}
        """
        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content

    @staticmethod
    def evaluate_analog_catalog_entries(analog_string: str, possible_catalog_entries: str) -> tuple[str, str]:
        gpt_manager = GPTModelManager()

        prompt = f"""  
        Du erhältst einen analog berechneten Leistungstext. Dazu bekommst du mögliche analog berechnende Leistungen aus dem Katalog selbstständiger zahnärztlicher
        gemäß § 6 Abs. 1 GOZ analog zu berechnender Leistungen der Bundes Zahnärzte Kammer (BZÄK). Passt der analog berechneten Leistungstext auf einen der mögliche analaog Berechnende Leistungen aus dem katalog 
        gib einen String in der folgenden Form zurück:       

        "Sektion": "Beschreibung"
        
        Regeln: 
        - Findest du keine übereinstimmung, so gib XXX_NOTHING_FOUND_XXX zurück
        - Du darfst ausschließlich dem String in der oben genannten Form antworten, oder mit XXX_NOTHING_FOUND_XXX.
        - Deine Rückgabe darf unter keinen Umständen andere Informationen enthalten.

        
        Analog berechneter Leistungstext:
        {analog_string}
        
        mögliche analog berechnende Leistungen aus dem Katalog der BZÄK:
        {possible_catalog_entries}
        """
        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content

    @staticmethod
    def write_analog_catalog_text_paragraph(analog_catalog_entry: str, invoice_text: str) -> tuple[str, str]:
        gpt_manager = GPTModelManager()

        prompt = f"""  
        
        Du erhältst einen Eintrag aus dem Katalog selbstständiger zahnärztlicher gemäß § 6 Abs. 1 GOZ analog zu berechnender Leistungen der Bundes Zahnärtze Kammer (BZÄK).
        
        Dieser Katalog definiert klar analog berechenbare Leistungen. 
        
        In einem Text der Krankenkasse wurde einem diese Leistung jedoch nicht als analog berechenbar beanstandet. Relativere die Aussage, der Krankenkasse mithilfe des Katalog Eintrags.
        
        Du bekommst als Info den Eintrag aus dem Katalog und den Rechnungstext der von der Krankenkasse beanstandet wurde.
                
        Regeln: 
        - Antworte in einem kurzem Paragraphen. 
        - Der Text benötigt keine Anrede oder ähnliches da dieser später noch zu einem vollständigen Text zusammen gesetzt wird.
        - Du darfst auf keinen Fall sagen, dass wir zu Rückfragen zur Verfügung stehen
        
        Eintrag aus dem Katalog:
        {analog_catalog_entry}
        
        Rechnungstext der von der Krankenkasse:
        {invoice_text}
        """
        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content

    @staticmethod
    def evaluate_analog_information(analog_input: str) -> tuple[str, bool]:
        gpt_manager = GPTModelManager()

        prompt = f"""  
        Du bekommst Rechnungspunkt eines Arztes. Prüfe ob es sich hier tatsächlich, um medizinische Inhalte handelt
        
        Regeln: 
        - Die Nachricht der Krankenkasse ist mit XXX_RECHNUNGS_TEXT_START_XXX und XXX_RECHNUNGS_TEXT_END_XXX gekennzeichnet. 
        - Antworte ausschließlich mit true oder false. Es darf nichts anderes als ein Boolean zurück gegeben werden.
        - Falls du dir nicht zu 100% sicher bist, tendiere eher mit true zu antworten
                    
                       
        XXX_RECHNUNGS_TEXT_START_XXX
        {analog_input}
        XXX_RECHNUNGS_TEXT_END_XXX
    
        """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content.lower() == "true"

    @staticmethod
    def evaluate_medical_necessity(insurance_text: str) -> tuple[str, bool]:
        gpt_manager = GPTModelManager()

        prompt = f"""  
        Du bekommst Rechnungspunkt eines Arztes. Prüfe ob hier die medizinische Notwendigkeit beanstandet wird
        
        Regeln: 
        - Die Nachricht der Krankenkasse ist mit XXX_INSURANCE_TEXT_START_XXX und XXX_INSURANCE_TEXT_END_XXX gekennzeichnet. 
        - Antworte ausschließlich mit true oder false. Es darf nichts anderes als ein Boolean zurück gegeben werden.
        - Falls in dem Text die medizinische Notwendigkeit beanstandet wird antworte mit true
        - Du darfst nur true zurück geben, wenn die medizinische Notwendigkeit wörtlich im Text erwähnt wird.
                    
                       
        XXX_INSURANCE_TEXT_START_XXX
        {insurance_text}
        XXX_INSURANCE_TEXT_END_XXX
    
        """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content.lower() == "true"

    @staticmethod
    def write_medical_necessity_text(insurance_text: str) -> tuple[str, str]:
        gpt_manager = GPTModelManager()

        medical_necessity_sample = """
        Der Bundesgerichtshof BGH hat in seinem Urteil (Az. IV ZR 151/90) die medizinische Notwendigkeit wie folgt definiert:
        "Die medizinische Notwendigkeit richtet sich nach objektiven und anerkannten ärztlichen Erkenntnissen. Sie ist dann gegeben, wenn und solange es nach den zur Zeit der Planung und Durchführung der Therapie erhobenen Befunden und den hierauf beruhenden ärztlichen Erkenntnissen vertretbar war, sie als notwendig anzusehen."
        Die medizinische Notwendigkeit kann folglich nur vom behandelnden Zahnarzt, nach objektiven fachlichen Kriterien beurteilt werden. Laut § 1 Abs. 2 GOZ (siehe auch Anlage) darf der Zahnarzt nur medizinisch notwendige Leistungen nach der GOZ berechnen. Medizinisch nicht notwendige Leistungen, die auf Verlangen des Patienten durchgeführt werden, müssen auf der Rechnung als solche bezeichnet werden (laut § 10 Abs. 3 Satz 7 GOZ).
        Bei der Beurteilung der Notwendigkeit einer Leistung kommt es auch darauf an, ob sie im gegebenen Fall eine langfristig sinnvolle Maßnahme darstellt, die dazu geeignet ist, die Funktionsfähigkeit des Kauorgans aufrechtzuerhalten bzw. wieder herzustellen. Unzweifelhaft ist, dass auf der Basis zahnmedizinisch-wissenschaftlicher Erkenntnisse, hierzu aufwendigere Versorgungen in der Regel besser geeignet sind als solche, die sich hauptsächlich an wirtschaftlichen Gesichtspunkten orientieren.
        """

        prompt = f"""  
        Du erhältst einen Mustertext der die Antwort auf eine Beanstandung der Krankenkasse darstellt, darüber hinaus erhälst du einen Text der Krankenkasse
        Regeln: 
        - Die Sektion für die medizinische Notwendigkeit ist durch XXX_MEDICAL_NECESSITY_TEXT_START_XXX und XXX_MEDICAL_NECESSITY_TEXT_END_XXX gekennzeichnet. 
        - Die Sektion für die Beanstandung der Krankenkasse ist durch XXX_INSURANCE_TEXT_START_XXX und XXX_INSURANCE_TEXT_END_XXX gekennzeichnet. 
        - Der Text der Krankenkasse beinhaltet die Beanstandung der medizinische Notwendigkeit
        - Schreibe einen Text mit Hilfe des MEDICAL_NECESSITY_TEXT der sich auf die Behandlung bezieht die in INSURANCE_TEXT beanstandet wird.
        - Der Text soll die Aussage der Krankenkasse durch die Informationen aus MEDICAL_NECESSITY_TEXT relativieren.
        - Der Text welchen du verfasst muss unbedingt die Informationsgehalt des MEDICAL_NECESSITY_TEXT beibehalten.
        - Der Text soll sich immer auf das Urteil des Bundesgerichtshof beziehen
        - Der Text benötigt keine Anrede oder ähnliches da dieser später noch zu einem vollständigen Text zusammen gesetzt wird.
        - Der Text ist jedoch an den Patienten gerichtet und nicht an die Krankenkasse. Hier soll dem Patienten nahegelegt werden, wieso die Beanstandung der Krankenkasse relativiert werden kann.
        - Der Text darf auf keinen Fall den Patienten auffordern, eine Handlung zu tätigen, es dient rein zur Information   
        - Du darfst nicht den Konjunktiv verwenden
        
            
        XXX_MEDICAL_NECESSITY_TEXT_START_XXX
        {medical_necessity_sample}
        XXX_MEDICAL_NECESSITY_TEXT_END_XXX
        
        XXX_INSURANCE_TEXT_START_XXX
        {insurance_text}
        XXX_INSURANCE_TEXT_END_XXX
        """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content

    @staticmethod
    def write_default_analog_text() -> tuple[str, str]:
        gpt_manager = GPTModelManager()

        default_analog_sample = """
        Die Paragrafen der Gebührenordnung bilden den gebührenrechtlichen Rahmen der GOZ. In der Anlage 1 zur GOZ sind die berechnungsfähigen Gebühren beschrieben, übergeordnet sind jedoch stets die GOZ-Paragrafen.
        Der § 6 Abs. 1 GOZ regelt die analoge Berechnung von selbstständigen zahnärztlichen Leistungen, die in der Gebührenordnung für Zahnärzte nicht enthalten sind. Für solche Leistungen kann eine nach Art, Kosten- und Zeitaufwand gleichwertige Leistung aus der GOZ herangezogen werden (siehe auch Anlage).
        Die Wahl einer nach Art, Kosten- und Zeitaufwand gleichwertigen Leistung obliegt allein dem Zahnarzt, denn nur er kann diese Faktoren bei der Ermittlung der Analogpositionen einschätzen und berücksichtigen.
        Da die Analogieberechnung im § 6 Abs. 1 GOZ explizit beschrieben ist, handelt es sich selbstverständlich um eine Berechnung im Rahmen der GOZ. 
        """

        prompt = f"""  
        Du erhältst einen Mustertext der die Antwort auf eine Beanstandung der Krankenkasse darstellt
        Regeln: 
        - Die Sektion für den Default Text ist durch XXX_DEFAULT_ANALOG_TEXT_START_XXX und XXX_DEFAULT_ANALOG_TEXT_END_XXX gekennzeichnet. 
        - Schreibe einen Text der sich an DEFAULT_ANALOG_TEXT orientiert.
        - Der Text benötigt keine Anrede oder ähnliches da dieser später noch zu einem vollständigen Text zusammen gesetzt wird.
            
        XXX_DEFAULT_ANALOG_TEXT_START_XXX
        {default_analog_sample}
        XXX_DEFAULT_ANALOG_TEXT_END_XXX
    
        """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content

    @staticmethod
    def write_already_covered_text(insurance_message: str) -> tuple[str, str]:
        gpt_manager = GPTModelManager()

        already_covered_sample = """
        "Es wurde eine selbstständige zahnärztliche Leistung erbracht, die kein Bestandteil einer anderen Leistung in der GOZ ist. 
        Selbstständige zahnärztliche Leistungen, die in das Gebührenverzeichnis nicht aufgenommen sind, können entsprechend einer nach Art, Kosten- und Zeitaufwand gleichwertigen Leistung des Gebührenverzeichnisses dieser Verordnung berechnet werden. 
        Bei der Auswahl einer Analogleistung müssen die individuelle Schwierigkeit, der Zeitaufwand sowie der Umfang der Leistung berücksichtigt werden. Auch der Kostenaufwand für die verbrauchten Materialien und verwendeten Geräte/Instrumente muss Berücksichtigung finden.
        Die Wahl einer nach Art, Kosten- und Zeitaufwand gleichwertigen Leistung obliegt allein dem Zahnarzt, denn nur er kann diese Faktoren bei der Ermittlung der Analogpositionen einschätzen und berücksichtigen.
        Natürlich kann es vorkommen, dass eine GOZ-Nummer nach ihrer Art mit der Analogleistung vergleichbar ist, aber nicht nach dem Kosten- und/oder Zeitaufwand.
        Es müssen aber alle Kriterien gleichermaßen miteinbezogen werden, um eine mit der Analogleistung am meisten vergleichbare GOZ-Nummer zu finden.
        Eine Versicherung ist aus fachlicher und gebührenrechtlicher Sicht nicht in der Lage eine gleichwertige GOZ-Nummer als Analogleistung heranzuziehen und deshalb auch nicht berechtigt diese vorzuschreiben."
        """

        prompt = f"""  
        Du erhältst einen Mustertext der eine Beanstandung einer Versicherung relativiert und eine Beanstandung einer Versicherung.
        Regeln: 
        - Der Muster Text ist mit XXX_ALREADY_COVERED_TEXT_START_XXX und XXX_ALREADY_COVERED_TEXT_END_XXX gekennzeichnet. 
        - Der Text der Versicherung ist mit XXX_INSURANCE_MESSAGE_TEXT_START_XXX und XXX_INSURANCE_MESSAGE_TEXT_END_XXX gekennzeichnet. 
        - Schreibe einen Text der auf Basis des ALREADY_COVERED_SAMPLE die Beanstandung der Versicherung relativiert
        - Der Text ist jedoch an den Patienten gerichtet und nicht an die Krankenkasse. Hier soll dem Patienten nahegelegt werden, wieso die Beanstandung der Krankenkasse relativiert werden kann.
        - Beziehe dich in dem Text auf die Behandlung die in INSURANCE_MESSAGE_TEXT beanstandet wird, da sie laut Versicherung bereits Bestandteil einer anderen Behandlung ist.
        - Der Text den du verfasst benötigt keine Anrede oder ähnliches da dieser später noch zu einem vollständigen Text zusammen gesetzt wird.
        - Rede hier bitte nicht von "unserer Leistung" stattdessen kannst du "die Leistung" sagen.
        - Der Text den du verfasst soll sich eng an den Argument aus ALREADY_COVERED_SAMPLE orientieren. 
        
        XXX_ALREADY_COVERED_TEXT_START_XXX
        {already_covered_sample}
        XXX_ALREADY_COVERED_TEXT_END_XXX
        
        XXX_INSURANCE_MESSAGE_TEXT_START_XXX
        {insurance_message}
        XXX_INSURANCE_MESSAGE_TEXT_END_XXX
        """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content

    @staticmethod
    def evaluate_judgment_text_analog(insurance_text: str) -> tuple[str, bool]:
        gpt_manager = GPTModelManager()

        prompt = f"""  
        Du bekommst eine Nachricht einer Krankenkasse in der ein Teil einer Rechnung beanstandet wird. 
        Prüfe ob die Krankenkasse hier die Faktoriesierung oder Faktorerhöhung beanstandet.
        
        Regeln: 
        - Die Nachricht der Krankenkasse ist mit XXX_INSURANCE_TEXT_START_XXX und XXX_INSURANCE_TEXT_END_XXX gekennzeichnet. 
        - Antworte ausschließlich mit true oder false. Es darf nichts anderes als ein Boolean zurück gegeben werden.
        - Die Antwort sollte true sein, wenn die Krankenkasse in irgendeiner Weise behauptet, dass es hier ein Problem 
          mit der Faktorisierung gibt oder auf Grund der Faktorisierung die Kosten nicht getragen werden.
        - Wenn keine Informationen über eine Faktorerhöhung oder eine Faktorisierung dem Text zu entnehmen sind ist mit false zu antworten.
                    
                       
        XXX_INSURANCE_TEXT_START_XXX
        {insurance_text}
        XXX_INSURANCE_TEXT_END_XXX
        
        """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content.lower() == "true"

    @staticmethod
    def write_judgment_text_analog() -> tuple[str, str]:
        gpt_manager = GPTModelManager()

        judgment_text_sample = """
        Der Bundesgerichtshof stellte mit dem Urteil vom 23.01.2003 fest, dass im Falle einer analogen Berechnung die Bestimmung zu § 10 Abs. 3 GOZ greift, wonach eine besondere Begründung erst bei Überschreiten des Schwellenwertes notwendig ist.
        Das Gericht führte aus: „Handelt es sich um eine analog berechenbare neue selbständige Leistung, ist die Honorierung über eine Nummer des Gebührenverzeichnisses nach Kriterien des § 6 Abs. 2 GOZ* vorzunehmen, die dann Grundlage für eine Anwendung des § 5 Abs. 2 GOZ ist.“
        Das Verwaltungsgericht Augsburg erklärte mit dem Urteil vom 08.06.2011, dass die reine analoge Berechnung von Leistungen nicht stets eine besondere Begründung voraussetzt. 
        Die analoge Berechnung hat bereits zur Voraussetzung, dass die tatsächlich erbrachte Leistung der in der GOZ beschriebenen Leistung, welche analog angewendet werden soll, nach Art, Kosten- und Zeitaufwand gleichwertig ist. 
        Die in der Gebührenposition beschriebene Leistung ist ein tauglicher Maßstab für die Bemessung der Gebühren. Deshalb gilt auch im Falle einer analogen Berechnung die eindeutige Bestimmung des § 10 Abs. 3 GOZ, demnach ist eine besondere Begründung erst bei Überschreiten des Schwellenwertes notwendig.
        """

        prompt = f"""  
        Du erhältst Urteils Texte, welche Rechtsprechungen bezüglich der analog Berechnung sind.
        Regeln: 
        - Die Urteils Sektion ist zwischen XXX_JUDGMENT_SAMPLE_START_XXX und XXX_JUDGMENT_SAMPLE_END_XXX gekennzeichnet. 
        - Fasse die Urteile zu einem Text zusammen, welcher die Urteile bezüglich der analogen Berechnung darstellt.
        - Der Text benötigt keine Anrede oder ähnliches da dieser später noch zu einem vollständigen Text zusammen gesetzt wird.
        
            
        XXX_JUDGMENT_SAMPLE_START_XXX
        {judgment_text_sample}
        XXX_JUDGMENT_SAMPLE_END_XXX
        """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content

    @staticmethod
    def evaluate_already_covered(insurance_text: str) -> tuple[str, bool]:
        gpt_manager = GPTModelManager()

        prompt = f"""  
        Du bekommst eine Nachricht einer Krankenkasse in der ein Teil einer Rechnung beanstandet wird. Prüfe ob hier explizit beanstandet wird,
        dass die genannte Leistung Bestandteil der Hauptziffer ist
        
        Regeln: 
        - Die Nachricht der Krankenkasse ist mit XXX_INSURANCE_TEXT_START_XXX und XXX_INSURANCE_TEXT_END_XXX gekennzeichnet. 
        - Antworte ausschließlich mit true oder false. Es darf nichts anderes als ein Boolean zurück gegeben werden.
        - Die Antwort sollte true sein, wenn die Krankenkasse behauptet, dass die Leistung bereits durch etwas anderes abgedeckt wird.
        - 
                    
                       
        XXX_INSURANCE_TEXT_START_XXX
        {insurance_text}
        XXX_INSURANCE_TEXT_END_XXX
        
        """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content.lower() == "true"

    @staticmethod
    def write_comment_text(insurance_message: str, comment: str) -> tuple[str, str]:
        gpt_manager = GPTModelManager()

        prompt = f"""  
        Du erhältst eine Beanstandung einer Krankenkasse und einen Kommentar der Bundeszahnärztekammer
        Regeln: 
        - Beginne deine Antwort IMMER mit "Im Kommentar der Bundeszahnärztekammer wird bestätigt"
        - Du musst in deiner Antwort IMMER erwähnen, dass diese Informationen aus dem Kommentar der Bundeszahnärztekammer stammen
        - Die Sektion für den Kommentar der Bundeszahnärztekammer ist durch XXX_COMMENT_START_XXX und XXX_COMMENT_END_XXX gekennzeichnet. 
        - Die Sektion für die Beanstandung der Krankenkasse ist durch XXX_INSURANCE_MESSAGE_TEXT_START_XXX und XXX_INSURANCE_MESSAGE_TEXT_END_XXX gekennzeichnet. 
        - Der Text der Krankenkasse beinhaltet die Beanstandung einer Leistung
        - Prüfe ob im Kommentar Informationen vorhanden sind, welche die Beanstandung der Krankenkasse relativieren, falls ja schreibe mit den Informationen welche die Beanstandung relativieren einen Text
        - Der Text soll die Aussage der Krankenkasse durch die Informationen aus comment relativieren.
        - Der Text darf NUR Informationen aus COMMENT enthalten, welche inhaltlich auf vorhandene Informationen in INSURANCE_MESSAGE bezogen werden können.
        - Sollten sich keine Information in COMMENT mit Bezug auf INSURANCE_MESSAGE befinden, gebe einen leeren String im Format '' zurück.
        - Du darfst NIE erwähnen wenn die Leistung eine Behandlung NICHT umfasst
        - Du darfst nur Informationen aus COMMENT benutzen, auf welche sich explizit in INSURANCE_MESSAGE bezogen wird.
        - Der Text benötigt keine Anrede oder ähnliches da dieser später noch zu einem vollständigen Text zusammen gesetzt wird.
        - Der Text darf auf keinen Fall den Patienten auffordern, eine Handlung zu tätigen, es dient rein zur Information
        - Du darfst nicht den Konjunktiv verwenden
    
    
    XXX_INSURANCE_MESSAGE_TEXT_START_XXX
    {insurance_message}
    XXX_INSURANCE_MESSAGE_TEXT_END_XXX
    
    XXX_COMMENT_START_XXX
    {comment}
    XXX_COMMENT_END_XXX
    

    """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content

    @staticmethod
    def shorten_text(text: str) -> tuple[str, str]:
        gpt_manager = GPTModelManager()

        prompt = f"""  
        Du erhältst einen Text den du kürzen musst.
        Regeln: 
        - Der Inhalt darf hierbei nicht verändert werden
        - Es dürfen NUR redundante Informationen entfernt werden, jedoch kannst du den Text kürzen, solange dessen Kernaussage nicht verändert wird
    
    Zu kürzender Text: 
    {text}
    """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content

    @staticmethod
    def find_matching_goz_keyword(keyword: str, goz_texts_dict: dict[str, str]) -> tuple[str, str]:
        gpt_manager = GPTModelManager()

        prompt = f"""  
        Du erhältst ein Keyword und eine Liste von GOZ Nummern mit zugehörigen Texten.
        Finde das Paar aus GOZ Nummer und Text, das am besten zum Keyword passt.
        Beachte dabei:
        - Das Keyword soll möglichst genau im Text der GOZ Nummer vorkommen oder am besten zum Kontext des Keywords passen.
        - Wähle nur ein Paar aus, das am besten passt.
        - Gebe das gefundene Paar mit zugehörigem Keyword im unten angegebenen Format zurück.
        - Gebe nur das unten gegebene Format zurück, nichts weiteres.
        - Wenn du kein Paar finden kannst, antworte nur mit XXX_NOTHING_FOUND_XXX
    
        Keyword Text: 
        {keyword}
        
        GOZ und Text Paare: 
        {goz_texts_dict}
        
        Gebe es in folgendem Format zurück
        "goz_nummer (keyword)"
        """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content

    @staticmethod
    def enrich_insurance_text(insurance_text: str, goz_keyword_list: str) -> tuple[str, str]:
        gpt_manager = GPTModelManager()

        prompt = f"""  
        Du erhältst einen Text einer Versicherung und eine Liste von GOZ Nummern mit Keyword.
        Finde in dem Text der Versicherung die Keywords aus der List und füge die GOZ Nummer dort hinzu
        Beachte dabei:
        - Der Text soll genau gleich bleiben nur die GOZ Nummern sollen ergänzt werden
        - Gebe nur den angepassten Text am Ende zurück, nichts anderes
    
        Das Format der GOZ Keyword Paart ist wie folgt
        "goz_nummer (keyword)"
        
        Text der Versicherung:
        {insurance_text}
        
        GOZ Keyword Paare: 
        {goz_keyword_list}
        
        Ersetze es in folgendem Format
        "Keyword (GOZ.Nr: GOZ Nummer)"
        """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content

    @staticmethod
    def evaluate_filling(insurance_text: str, invoice_text: str) -> tuple[str, bool]:
        gpt_manager = GPTModelManager()

        prompt = f"""  
            Überprüfe, ob der folgende Text der Krankenkasse oder der Rechnungstext die GOZ Nr 2180 enthält, oder/und sich auf die Behandlung "Aufbaufüllung aufwend. Mehrschichttechnik" bezieht.
            
            Regeln: 
            - Antworte ausschließlich mit true oder false. Es darf nichts anderes als ein Boolean zurück gegeben werden.
            - Es muss entweder die GOZ-Nr. 2180 oder die Behandlung "Aufbaufüllung aufwend. Mehrschichttechnik" im Text der Krankenkasse oder im Rechnungstext erwähnt werden. Es genügt, wenn eine der beiden Bedingungen in einem der Texte erfüllt ist, um mit "true" zu antworten.

            Text der Krankenkasse:
            {insurance_text}
            
            Rechnungstext: 
            {invoice_text}
            
            """
        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content.lower() == "true"

    @staticmethod
    def write_filling_sample_text() -> tuple[str, str]:
        gpt_manager = GPTModelManager()

        filling_sample_text = """
        Ihre Versicherung behauptet, dass eine dentinadhäsive Aufbaufüllung in Mehrschichttechnik nach der GOZ-Nr. 2180 berechnungsfähig sei, da es sich um eine Aufbaufüllung zur Aufnahme einer Krone handele.
        Die GOZ-Nr. 2180 beschreibt eine einfache Aufbaufüllung mit plastischen Materialien, die Mehrschichttechnik ist nicht in den Leistungsbeschreibungen der GOZ-Nrn. 2180 und 2197 genannt. Da die Mehrschichttechnik den Hauptbestandteil der Leistung darstellt, handelt es sich somit um eine Leistung, die in der GOZ nicht beschrieben ist. Alle Voraussetzungen für eine Analogberechnung gemäß § 6 Abs. 1 GOZ sind erfüllt, wenn folgende Kriterien zutreffen:
        es handelt sich um eine selbstständige zahnärztliche Leistung
        die Leistung ist weder in der GOZ noch in der GOÄ vorhanden (auch nicht als Bestandteil oder besondere Ausführung einer Leistung aus der GOZ oder GOÄ)
        Die Berechnung der Analogleistung ist somit korrekt erfolgt und wird auch durch nachfolgende Urteile rechtlich bestätigt:
        AG Weinheim (Az. 1 C 140/17), 10.01.2019
        LG Stuttgart (Az. 22 O 171/16), 02.03.2018
        AG Berlin-Schöneberg (Az. 18 C 65/14), 05.05.2015
        AG Berlin-Charlottenburg (Az. 205 C 13/12), 08.05.2014
        """

        prompt = f"""  
        Du erhältst einen Mustertext der die Antwort auf eine Beanstandung der Krankenkasse darstellt
        Regeln: 
        - Die Sektion für den Default Text ist durch XXX_FILLING_SAMPLE_TEXT_START_XXX und XXX_FILLING_SAMPLE_TEXT_END_XXX gekennzeichnet. 
        - Schreibe einen Text der sich an FILLING_SAMPLE_TEXT orientiert.
        - Der Text benötigt keine Anrede oder ähnliches da dieser später noch zu einem vollständigen Text zusammen gesetzt wird.
        - Der Text ist jedoch an den Patienten gerichtet und nicht an die Krankenkasse. Hier soll dem Patienten nahegelegt werden, wieso die Beanstandung der Krankenkasse relativiert werden kann.
        - Die Markierung der Sektionen wie z.B XXX_FILLING_SAMPLE_TEXT_START_XXX darf nicht im Text enthalten sein.
        - Rede hier bitte nicht von "unserer Leistung" stattdessen kannst du "die Leistung" sagen.
        - Du darfst auf keinen Fall sagen, dass wir zu Rückfragen zur Verfügung stehen
        - Erwähne auf jeden Fall die im XXX_FILLING_SAMPLE_TEXT_START_XXX enthaltenen Urteile
            
        XXX_FILLING_SAMPLE_TEXT_START_XXX
        {filling_sample_text}
        XXX_FILLING_SAMPLE_TEXT_END_XXX
    
        """

        response = gpt_manager.CHAT_GPT_4_TEMP_0([HumanMessage(content=prompt)])

        return prompt, response.content
