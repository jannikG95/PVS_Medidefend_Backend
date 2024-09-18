import json

from autoresponder.services.relativization_service import RelativizationService
from autoresponder.util.model_helper import ModelHelper
from autoresponder.util.pinecone_service import PineconeService
from autoresponder.util.prompt_service import PromptService
from autoresponder.util.utility_service import UtilityService


class RegularService(RelativizationService):

    def process_regular_case(self, generated_record, insurance_text):
        if not insurance_text:
            self.update_error_status(generated_record, "Kein Input String")
            return

        possible_sample_answers = []
        possible_judgments_answers = []
        medical_necessity_text = ''
        comment_text = ''
        judgement_text = ''
        sample_text = ''

        # Special case 1: hard check: Für diese Aufwendungen sieht der Tarif keine Leistungen vor.
        no_tariff_benefit_text = self.check_not_in_tariff(insurance_text)
        # if it's a no_tariff_benefit_case there is no need to keep on generating more texts
        if not no_tariff_benefit_text:

            prompt, extracted_regular_keywords = PromptService.extract_regular_keywords_from_string_to_json(
                insurance_text)
            self.cost_service.add_io_tokens(prompt, extracted_regular_keywords)
            enriched_insurance_text = self.generate_enriched_insurance_text(extracted_regular_keywords, insurance_text)

            if enriched_insurance_text:
                insurance_text = enriched_insurance_text

            medical_necessity_text = self.check_medical_necessity(insurance_text)

            prompt, extracted_goz_number = PromptService.extract_goz_number_from_string(insurance_text)
            self.cost_service.add_io_tokens(prompt, extracted_goz_number)
            self.update_status(generated_record, "20", "Detected GOZ number: " + extracted_goz_number)

            self.update_status(generated_record, "30", "[IN PROGRESS] - fetch_samples_and_comment_for_goz")
            associated_samples, comment = self.fetch_samples_and_comment_for_goz(extracted_goz_number)

            self.update_status(generated_record, "35", "[IN PROGRESS] - generate_comment_text")
            comment_text = self.generate_comment_text(insurance_text, comment)

            self.update_status(generated_record, "40", "[IN PROGRESS] - find_relevant_sample_titles ")
            relevant_sample_titles = self.find_relevant_sample_titles(insurance_text, associated_samples)

            self.update_status(generated_record, "50", "[IN PROGRESS] - find_relevant_samples")
            relevant_samples = self.find_relevant_samples(insurance_text, relevant_sample_titles or associated_samples)

            self.update_status(generated_record, "55", "[IN PROGRESS] - generate_possible_answers")
            possible_sample_answers = self.generate_possible_answers(insurance_text, relevant_samples, 'mustertext')

            self.update_status(generated_record, "60", "[IN PROGRESS] - get_urteile_for_goz")
            associated_judgments = ModelHelper.get_urteile_for_goz(goz_nummer=extracted_goz_number)

            self.update_status(generated_record, "70", "[IN PROGRESS] - find_relevant_judgment_titles")
            relevant_judgment_title = self.find_relevant_judgment_titles(insurance_text, associated_judgments)

            self.update_status(generated_record, "75", "[IN PROGRESS] - find_relevant_judgements")
            relevant_judgments = self.find_relevant_judgments(insurance_text,
                                                              relevant_judgment_title or associated_judgments)

            self.update_status(generated_record, "80", "[IN PROGRESS] - generate_possible_judgments_answers")
            possible_judgments_answers = self.generate_possible_judgments_answers(insurance_text, relevant_judgments)

            if possible_judgments_answers:
                judgement_text = self.generate_judgement_text(insurance_text, possible_judgments_answers)

            if possible_sample_answers:
                sample_text = self.generate_sample_text(insurance_text, possible_sample_answers)

            # Special case 1: soft check: Für diese Aufwendungen sieht der Tarif keine Leistungen vor.
            if not no_tariff_benefit_text.strip():
                prompt, response = PromptService.evaluate_no_tariff_benefit_soft(insurance_text)
                self.cost_service.add_io_tokens(prompt, str(response))
                if response:
                    prompt, no_tariff_benefit_text = PromptService.write_tariff_benefit_text()
                    self.cost_service.add_io_tokens(prompt, no_tariff_benefit_text)

        if self.invalid_response_or_missing_goz(generated_record, possible_sample_answers, possible_judgments_answers,
                                                no_tariff_benefit_text, medical_necessity_text, comment_text):
            return

        opening_text = self.generate_opening_text(insurance_text)
        if no_tariff_benefit_text:
            closing_text = self.generate_closing_text_no_tariff_benefit()
        else:
            closing_text = self.generate_closing_text()

        self.update_status(generated_record, "90", "[IN PROGRESS] - write_final_response")

        texts = [sample_text, judgement_text, no_tariff_benefit_text, medical_necessity_text, comment_text]
        shortened_texts = self.shorten_texts(texts)
        regular_answer = self.generate_answer(opening_text, closing_text, shortened_texts)

        self.update_success_status(generated_record, regular_answer)
        return

    def generate_enriched_insurance_text(self, extracted_regular_keywords, insurance_text):
        if extracted_regular_keywords != "XXX_NOTHING_FOUND_XXX":
            extracted_regular_keywords_json = json.loads(extracted_regular_keywords)
            if len(extracted_regular_keywords_json) > 1:
                goz_keyword_list = self.check_input_gozs(extracted_regular_keywords_json)
                if goz_keyword_list:
                    prompt, enriched_insurance_text = PromptService.enrich_insurance_text(insurance_text,
                                                                                          goz_keyword_list)
                    self.cost_service.add_io_tokens(prompt, enriched_insurance_text)
                    return enriched_insurance_text
        return ''

    def check_input_gozs(self, regular_keywords) -> list[str]:
        goz_keyword_list = []
        for keyword in regular_keywords:
            pinecone_goz_matches_dict = {}
            matches = PineconeService.similarity_search(query_text=keyword, namespace="goz", top_k=5)
            for match in matches:
                metadata = match.get('metadata', {})
                goz_number = metadata.get('goz_number', None)
                goz_text = metadata.get('goz_text', None)
                if goz_number:
                    pinecone_goz_matches_dict[goz_number] = goz_text
            prompt, matching_goz_keyword = PromptService.find_matching_goz_keyword(keyword, pinecone_goz_matches_dict)
            self.cost_service.add_io_tokens(prompt, matching_goz_keyword)
            goz_keyword_list.append(matching_goz_keyword)

        if goz_keyword_list:
            return [item for item in goz_keyword_list if "XXX_NOTHING_FOUND_XXX" not in item]
        return []

    def check_not_in_tariff(self, insurance_text):
        prompt, response = PromptService.evaluate_no_tariff_benefit_hard(insurance_text)
        self.cost_service.add_io_tokens(prompt, str(response))
        if response:
            prompt, response = PromptService.write_tariff_benefit_text()
            self.cost_service.add_io_tokens(prompt, response)
            return response
        return ''

    def check_medical_necessity(self, insurance_text):
        prompt, response = PromptService.evaluate_medical_necessity(insurance_text)
        self.cost_service.add_io_tokens(prompt, str(response))
        if response:
            prompt, response = PromptService.write_medical_necessity_text(insurance_text)
            self.cost_service.add_io_tokens(prompt, response)
            return response
        return ''

    def find_relevant_sample_titles(self, insurance_text, associated_samples):
        relevant_sample_titles = []
        for sample in associated_samples:
            sample_title = sample.get('titel', '')
            prompt, response = PromptService.evaluate_muster_title_for_message(insurance_text, sample_title)
            self.cost_service.add_io_tokens(prompt, str(response))
            if response:
                relevant_sample_titles.append(sample)
        return relevant_sample_titles

    def find_relevant_samples(self, insurance_text, relevant_sample_titles):
        relevant_samples = []
        for index, sample in enumerate(relevant_sample_titles):
            sample_text = sample.get('mustertext', '')
            prompt, response = PromptService.evaluate_muster_text_for_message(insurance_text, sample_text)
            self.cost_service.add_io_tokens(prompt, str(response))
            if response:
                relevant_samples.append(sample)
        return relevant_samples

    def find_relevant_judgment_titles(self, insurance_text, associated_judgments):
        relevant_judgment_title = []
        for urteil in associated_judgments:
            urteil_title = urteil.get('titel', '')
            prompt, response = PromptService.evaluate_urteils_title_for_message(insurance_text, urteil_title)
            self.cost_service.add_io_tokens(prompt, str(response))
            if response:
                relevant_judgment_title.append(urteil)
        return relevant_judgment_title

    def find_relevant_judgments(self, insurance_text, relevant_judgment_title):
        relevant_judgments = []
        for index, urteil in enumerate(relevant_judgment_title):
            urteil_text = urteil.get('urteiltext', '')
            prompt, response = PromptService.evaluate_judgment_text_for_message(insurance_text,
                                                                                UtilityService.cut_string_to_length(
                                                                                    urteil_text))
            self.cost_service.add_io_tokens(prompt, str(response))
            if response:
                relevant_judgments.append(urteil)
        return relevant_judgments

    def generate_possible_answers(self, insurance_text, items, text_attribute):
        possible_answers = []
        for item in items:
            item_text = item.get(text_attribute, '')
            prompt, response = PromptService.write_response_from_sample_text(insurance_text, item_text)
            self.cost_service.add_io_tokens(prompt, response)
            if response:
                possible_answers.append(response)
        return possible_answers

    def generate_possible_judgments_answers(self, insurance_text, relevant_judgments):
        possible_judgments_answers = []
        for urteil in relevant_judgments:
            urteil_text = urteil.get('urteiltext', '')
            prompt, response = PromptService.write_response_from_urteils_text(insurance_text,
                                                                              UtilityService.cut_string_to_length(
                                                                                  urteil_text))
            self.cost_service.add_io_tokens(prompt, response)
            if response:
                possible_judgments_answers.append(response)
        return possible_judgments_answers

    def invalid_response_or_missing_goz(self, generated_record, possible_answers, possible_judgments_answers,
                                        no_tariff_benefit_text, medical_necessity_text, comment_text):
        if not (possible_answers or possible_judgments_answers or no_tariff_benefit_text.strip()
                or medical_necessity_text.strip() or comment_text.strip()):
            self.update_error_status(generated_record,
                                     "Zu ihrer Beanstandung konnte keine korrekte Antwort generiert werden")
            return True
        return False

    def generate_comment_text(self, insurance_text, comment):
        if comment.strip():
            prompt, response = PromptService.write_comment_text(insurance_text, comment)
            self.cost_service.add_io_tokens(prompt, response)
            return response
        return ''

    def generate_judgement_text(self, insurance_text, judgments_answers: list[str]):
        prompt, response = PromptService.write_judgement_answer_text(insurance_text, judgments_answers)
        self.cost_service.add_io_tokens(prompt, response)
        return response

    def generate_sample_text(self, insurance_text, sample_answers: list[str]):
        prompt, response = PromptService.write_sample_answer_text(insurance_text, sample_answers)
        self.cost_service.add_io_tokens(prompt, response)
        return response

    def fetch_samples_and_comment_for_goz(self, extracted_goz_number):
        if extracted_goz_number == "XXX_NOTHING_FOUND_XXX":
            return [], ''

        associated_samples = ModelHelper.get_muster_for_goz(goz_nummer=extracted_goz_number)
        comment = ModelHelper.get_comment_for_goz(goz_nummer=extracted_goz_number)

        return associated_samples, comment

    def generate_closing_text_no_tariff_benefit(self):
        return "Ich hoffe, dass diese Informationen hilfreich für Sie sind und stehe für weitere Rückfragen zur Verfügung.\n\nMit freundlichen Grüßen"

    def shorten_texts(self, texts):
        texts = [text for text in texts if text]
        shortened_texts = []

        for text in texts:
            prompt, response = PromptService.shorten_text(text)
            self.cost_service.add_io_tokens(prompt, response)
            shortened_texts.append(response)

        return shortened_texts
