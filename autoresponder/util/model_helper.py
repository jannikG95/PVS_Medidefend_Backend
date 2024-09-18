from typing import List, Dict

from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404

from autoresponder.models import GOZ, GOZ_Muster, GOZ_Urteile


class ModelHelper:

    @staticmethod
    def get_goz_details_as_dict(goz_nummer: str) -> dict:
        """
        Gibt die Details einer GOZ-Instanz als Dictionary zurück.

        Diese Funktion sucht eine GOZ-Instanz basierend auf der übergebenen
        goz_nummer. Wenn die Instanz gefunden wird, wird sie in ein Dictionary
        konvertiert und zurückgegeben. Falls keine Instanz mit der angegebenen
        goz_nummer gefunden wird, wird eine 404-Fehlerantwort ausgelöst.

        Args:
            goz_nummer (str): Die Nummer der GOZ-Instanz, die abgefragt werden soll.

        Returns:
            dict: Ein Dictionary, das die Details der gefundenen GOZ-Instanz enthält.

        Raises:
            Http404: Wenn keine GOZ-Instanz mit der angegebenen goz_nummer gefunden wird.
        """
        # Holen Sie die GOZ-Instanz mit der spezifischen goz_nummer
        goz = get_object_or_404(GOZ, goz_nummer=goz_nummer)

        # Konvertieren Sie die GOZ-Instanz in ein Dictionary
        goz_details = model_to_dict(goz)

        return goz_details

    @staticmethod
    def get_muster_for_goz(goz_nummer: str) -> List[Dict]:
        """
        Gibt eine Liste von Mustern als Dictionaries zurück, die mit einer gegebenen GOZ-Nummer verknüpft sind.

        Diese Funktion sucht zunächst das GOZ-Objekt, das der übergebenen goz_nummer entspricht. Falls das GOZ-Objekt existiert,
        werden alle mit ihm verknüpften GOZ_Muster Objekte gesucht. Jedes gefundene Muster wird in ein Dictionary umgewandelt,
        wobei der 'mustertext' jedes Musters durch eine spezifische Methode dekodiert wird, bevor es der Rückgabeliste hinzugefügt wird.
        Falls kein GOZ-Objekt für die gegebene goz_nummer gefunden wird, gibt die Funktion eine leere Liste zurück.

        Args:
            goz_nummer (str): Die Nummer der GOZ-Instanz, für die Muster gefunden werden sollen.

        Returns:
            List[Dict]: Eine Liste von Dictionaries, wobei jedes Dictionary Details eines Musters enthält.
        """
        try:
            # Finde das GOZ-Objekt basierend auf der goz_nummer
            goz = GOZ.objects.get(goz_nummer=goz_nummer)
        except GOZ.DoesNotExist:
            # Falls kein GOZ-Objekt gefunden wird, gibt eine leere Liste zurück
            return []

        # Finde alle GOZ_Muster, die mit dem gefundenen GOZ-Objekt verknüpft sind
        goz_muster_list = GOZ_Muster.objects.filter(goz=goz)

        # Konvertiere jedes Muster in ein Dictionary und dekodiere den mustertext
        muster_dict_list = []
        for gm in goz_muster_list:
            muster_dict = model_to_dict(gm.muster)
            muster_dict_list.append(muster_dict)

        return muster_dict_list

    @staticmethod
    def get_comment_for_goz(goz_nummer: str) -> str:
        """
        Gibt ein Kommentar zu einer zugehörigen GOZ Nummer zurück, falls keine gefunden wird gibt er ein leeren String zurück

        Args:
            goz_nummer (str): Die Nummer der GOZ-Instanz, für die das Kommentar gefunden werden sollen.

        Returns:
            str: Ein String der das Kommentar enthält
        """
        try:
            # Finde das GOZ-Objekt basierend auf der goz_nummer
            goz = GOZ.objects.get(goz_nummer=goz_nummer)
        except GOZ.DoesNotExist:
            # Falls kein GOZ-Objekt gefunden wird, gibt eine leere Liste zurück
            return ''

        return goz.kommentare

    @staticmethod
    def get_urteile_for_goz(goz_nummer: str) -> List[Dict]:
        """
        Gibt eine Liste von Urteilen als Dictionaries zurück, die mit einer gegebenen GOZ-Nummer verknüpft sind.

        Diese Funktion sucht zunächst das GOZ-Objekt, das der übergebenen goz_nummer entspricht. Falls das GOZ-Objekt existiert,
        werden alle mit ihm verknüpften GOZ_Urteile Objekte gesucht. Jedes gefundene Urteil wird in ein Dictionary umgewandelt und
        der Rückgabeliste hinzugefügt. Falls kein GOZ-Objekt für die gegebene goz_nummer gefunden wird, gibt die Funktion eine
        leere Liste zurück.

        Args:
            goz_nummer (str): Die Nummer der GOZ-Instanz, für die Urteile gefunden werden sollen.

        Returns:
            List[Dict]: Eine Liste von Dictionaries, wobei jedes Dictionary Details eines Urteils enthält.
        """
        try:
            # Finde das GOZ-Objekt basierend auf der goz_nummer
            goz = GOZ.objects.get(goz_nummer=goz_nummer)
        except GOZ.DoesNotExist:
            # Falls kein GOZ-Objekt gefunden wird, gibt eine leere Liste zurück
            return []

        # Finde alle GOZ_Urteile, die mit dem gefundenen GOZ-Objekt verknüpft sind
        goz_urteile_list = GOZ_Urteile.objects.filter(goz=goz)

        # Konvertiere jedes Urteil in ein Dictionary und erstelle eine Liste dieser Dictionaries
        urteile_dict_list = [model_to_dict(urteil) for urteil in goz_urteile_list]

        return urteile_dict_list
