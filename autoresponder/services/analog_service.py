from autoresponder.services.relativization_service import RelativizationService
from autoresponder.util.pinecone_service import PineconeService
from autoresponder.util.prompt_service import PromptService


class AnalogService(RelativizationService):

    def process_analog_case(self, generated_record, insurance_text, invoice_text):
        generated_record.analog_input = invoice_text
        generated_record.save()

        prompt, response = PromptService.evaluate_analog_information(invoice_text)
        self.cost_service.add_io_tokens(prompt, str(response))

        if not response:
            self.update_error_status(generated_record, "Es konnten keine passenden Daten zur Analogberechnung in Ihrem Text gefunden werden")
            return

        self.update_status(generated_record, "20", "[IN PROGRESS] - extract_keywords_from_string_to_json")
        prompt, extracted_analog_keyword = PromptService.extract_analog_keywords_from_string_to_json(invoice_text)
        self.cost_service.add_io_tokens(prompt, extracted_analog_keyword)

        filling_sammple_text = self.generate_filling_sample_text(insurance_text, invoice_text)

        self.update_status(generated_record, "30", "[IN PROGRESS] - generate_analog_catalog_text")
        analog_catalog_text = self.generate_analog_catalog_text(invoice_text, extracted_analog_keyword)

        self.update_status(generated_record, "40", "[IN PROGRESS] - write_default_analog_text")
        prompt, default_analog_text = PromptService.write_default_analog_text()
        self.cost_service.add_io_tokens(prompt, default_analog_text)

        self.update_status(generated_record, "50", "[IN PROGRESS] - generate_medical_necessity_text")
        medical_necessity_text = self.generate_medical_necessity_text(insurance_text)

        self.update_status(generated_record, "60", "[IN PROGRESS] - generate_judgment_text_analog")
        judgment_text_analog = self.generate_judgment_text_analog(insurance_text)

        self.update_status(generated_record, "70", "[IN PROGRESS] - generate_already_covered_text")
        already_covered_text = self.generate_already_covered_text(insurance_text)

        if default_analog_text == '':
            self.update_error_status(generated_record, "Es konnte keine Antwort generiert werden.")
            return

        self.update_status(generated_record, "80", "[IN PROGRESS] - write_analog_answer")

        opening_text = self.generate_opening_text(insurance_text)
        closing_text = self.generate_closing_text()

        self.update_status(generated_record, "90", "[IN PROGRESS] - write_analog_answer")

        texts = [default_analog_text, medical_necessity_text, already_covered_text, filling_sammple_text, judgment_text_analog, analog_catalog_text]
        shortened_texts = self.shorten_texts(texts)
        analog_answer = self.generate_answer(opening_text, closing_text, shortened_texts)

        self.update_success_status(generated_record, analog_answer)
        return

    def generate_filling_sample_text(self, insurance_text, invoice_text):
        prompt, filling_edgecase = PromptService.evaluate_filling(insurance_text, invoice_text)
        self.cost_service.add_io_tokens(prompt, str(filling_edgecase))
        if filling_edgecase:
            prompt, filling_sample_text = PromptService.write_filling_sample_text()
            self.cost_service.add_io_tokens(prompt, filling_sample_text)
            return filling_sample_text
        return ''

    def generate_analog_catalog_text(self, invoice_text, extracted_analog_keyword) -> str:
        if extracted_analog_keyword != "XXX_NOTHING_FOUND_XXX":
            matches = PineconeService.similarity_search(query_text=extracted_analog_keyword, top_k=3)
            possible_catalog_entries = ""
            for match in matches:
                metadata = match.get('metadata', {})
                section = metadata.get('section', None)
                sentence = metadata.get('sentence', None)

                possible_catalog_entries += "Sektion: " + section + "\n" + "Beschreibung: " + sentence + "\n\n--------------\n"

            prompt, analog_catalog_entry = PromptService.evaluate_analog_catalog_entries(invoice_text, possible_catalog_entries)
            self.cost_service.add_io_tokens(prompt, analog_catalog_entry)

            if analog_catalog_entry != "XXX_NOTHING_FOUND_XXX":
                prompt, response = PromptService.write_analog_catalog_text_paragraph(analog_catalog_entry=analog_catalog_entry, invoice_text=invoice_text)
                self.cost_service.add_io_tokens(prompt, response)
                return response
            else:
                return ''
        else:
            return ''

    def generate_medical_necessity_text(self, insurance_text):
        prompt, response = PromptService.evaluate_medical_necessity(insurance_text)
        self.cost_service.add_io_tokens(prompt, str(response))
        if response:
            prompt, response = PromptService.write_medical_necessity_text(insurance_text)
            self.cost_service.add_io_tokens(prompt, response)
            return response
        else:
            return ''

    def generate_judgment_text_analog(self, insurance_text):
        prompt, response = PromptService.evaluate_judgment_text_analog(insurance_text)
        self.cost_service.add_io_tokens(prompt, str(response))
        if response:
            prompt, response = PromptService.write_judgment_text_analog()
            self.cost_service.add_io_tokens(prompt, response)
            return response
        else:
            return ''

    def generate_already_covered_text(self, insurance_text):
        prompt, response = PromptService.evaluate_already_covered(insurance_text)
        self.cost_service.add_io_tokens(prompt, str(response))
        if response:
            prompt, response = PromptService.write_already_covered_text(insurance_text)
            self.cost_service.add_io_tokens(prompt, response)
            return response
        else:
            return ''

