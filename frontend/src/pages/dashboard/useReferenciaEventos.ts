import { useEffect, useState } from "react";

import { toApiErrorMessage } from "../../services/http";
import { listReferenciaEventos, type ReferenciaEvento } from "../../services/leads_import";

type UseReferenciaEventosResult = {
  eventOptions: ReferenciaEvento[];
  isLoadingEvents: boolean;
  eventsError: string | null;
};

export function useReferenciaEventos(token: string | null | undefined): UseReferenciaEventosResult {
  const [eventOptions, setEventOptions] = useState<ReferenciaEvento[]>([]);
  const [isLoadingEvents, setIsLoadingEvents] = useState(false);
  const [eventsError, setEventsError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;

    let isActive = true;
    setIsLoadingEvents(true);
    setEventsError(null);

    listReferenciaEventos(token)
      .then((response) => {
        if (!isActive) return;
        setEventOptions(response);
      })
      .catch((requestError) => {
        if (!isActive) return;
        setEventsError(toApiErrorMessage(requestError, "Nao foi possivel carregar os eventos."));
      })
      .finally(() => {
        if (isActive) {
          setIsLoadingEvents(false);
        }
      });

    return () => {
      isActive = false;
    };
  }, [token]);

  return {
    eventOptions,
    isLoadingEvents,
    eventsError,
  };
}
