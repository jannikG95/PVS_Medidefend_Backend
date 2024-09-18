import logging
from .cost_service import CostService
from ..util.prompt_service import PromptService

logger = logging.getLogger('RealtivizationService')

class RelativizationService:

    def __init__(self):
        self.cost_service = CostService()

    def update_status(self, generated_record, status, log_message):
        logger.info(log_message + " - Status: " + status)
        generated_record.status = status
        generated_record.save()

    def update_error_status(self, generated_record, error_output):
        generated_record.status = 'ERROR'
        generated_record.output = error_output
        costs = self.cost_service.calculate_total_request_costs()
        generated_record.costs = costs
        logger.error('[FAILED] An error occurred: %s', error_output)
        logger.info('[TOTAL COSTS] ---- %s', costs)
        generated_record.save()

    def update_success_status(self, generated_record, response):
        generated_record.status = "SUCCESS"
        generated_record.output = response
        costs = self.cost_service.calculate_total_request_costs()
        generated_record.costs = costs
        logger.info('[COMPLETED] Record processed successfully')
        logger.info('[TOTAL COSTS] ---- %s', costs)
        generated_record.save()

    def generate_opening_text(self, insurance_text):
        prompt, response = PromptService.write_opening_text(insurance_text)
        self.cost_service.add_io_tokens(prompt, response)
        return response

    def generate_answer(self, opening_text, closing_text, shortened_texts: list[str]):

        result = opening_text
        for text in shortened_texts:
            result += "\n\n" + text

        result += "\n\n" + closing_text

        return result

    def shorten_texts(self, texts):
        texts = [text for text in texts if text]
        shortened_texts = []

        for text in texts:
            prompt, response = PromptService.shorten_text(text)
            self.cost_service.add_io_tokens(prompt, response)
            shortened_texts.append(response)

        return shortened_texts

    def generate_closing_text(self):
        return "Ich hoffe, dass mit diesen Informationen der Erstattung aller erbrachten und verordnungskonform berechneten Leistungen nichts mehr im Wege steht. Sie können diese Informationen Ihrer kostenerstattenden Stelle zur Prüfung auf nachträgliche tarifliche Erstattung weiterleiten.\n\nMit freundlichen Grüßen"
