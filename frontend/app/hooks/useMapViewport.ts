import {

  useCallback,

  useEffect,

  useLayoutEffect,

  useMemo,

  useRef,

  useState,

  type RefObject,

} from "react";



import {

  clampTranslate,

  clampUserScale,

  computeCenteredTransform,

  computeDisplayScale,

  computeFitScale,

  screenToMap,

  viewportTransformStyle,

  zoomAtPoint,

  type FitMode,

  type Size,

  type ViewportTransform,

} from "../lib/mapViewportMath";



export type UseMapViewportOptions = {

  mapSize: Size;

  enabled?: boolean;

  fitMode?: FitMode;

};



export type UseMapViewportResult = {

  viewportRef: RefObject<HTMLDivElement | null>;

  userScale: number;

  translateX: number;

  translateY: number;

  displayScale: number;

  fitScale: number;

  isPanning: boolean;

  transformStyle: string;

  transformTransition?: string;

  cursorClassName: string;

  resetViewport: (options?: ViewportResetOptions) => void;

  screenToMapFromClient: (

    clientX: number,

    clientY: number

  ) => { x: number; y: number } | null;

};



export type ViewportResetOptions = {

  animated?: boolean;

};



const VIEWPORT_RESET_TRANSITION_MS = 200;

const VIEWPORT_RESET_TRANSITION = `transform ${VIEWPORT_RESET_TRANSITION_MS}ms ease-out`;



const INITIAL_TRANSFORM: ViewportTransform = {

  userScale: 1,

  translateX: 0,

  translateY: 0,

};



function isMiddleMouseButton(event: MouseEvent): boolean {

  return event.button === 1;

}



export function readViewportSize(element: HTMLElement): Size {

  const rect = element.getBoundingClientRect();

  return { w: rect.width, h: rect.height };

}



export function useMapViewport({

  mapSize,

  enabled = true,

  fitMode = "cover",

}: UseMapViewportOptions): UseMapViewportResult {

  const viewportRef = useRef<HTMLDivElement | null>(null);

  const [viewportSize, setViewportSize] = useState<Size>({ w: 0, h: 0 });

  const [transform, setTransform] = useState<ViewportTransform>(INITIAL_TRANSFORM);

  const [isPanning, setIsPanning] = useState(false);

  const [isResetAnimating, setIsResetAnimating] = useState(false);



  const transformRef = useRef(transform);

  transformRef.current = transform;



  const viewportSizeRef = useRef(viewportSize);

  viewportSizeRef.current = viewportSize;



  const mapSizeRef = useRef(mapSize);

  mapSizeRef.current = mapSize;



  const fitModeRef = useRef(fitMode);

  fitModeRef.current = fitMode;



  const panStateRef = useRef<{

    startClientX: number;

    startClientY: number;

    startTranslateX: number;

    startTranslateY: number;

  } | null>(null);



  const resetTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);



  const clearResetAnimation = useCallback(() => {

    if (resetTimerRef.current !== null) {

      clearTimeout(resetTimerRef.current);

      resetTimerRef.current = null;

    }

    setIsResetAnimating(false);

  }, []);



  const fitScale = useMemo(

    () => computeFitScale(viewportSize, mapSize, fitMode),

    [viewportSize, mapSize, fitMode]

  );



  const displayScale = useMemo(

    () => computeDisplayScale(fitScale, transform.userScale),

    [fitScale, transform.userScale]

  );



  const applyClampedTransform = useCallback((next: ViewportTransform): ViewportTransform => {

    const viewport = viewportSizeRef.current;

    const map = mapSizeRef.current;

    const nextFitScale = computeFitScale(viewport, map, fitModeRef.current);

    const clampedUserScale = clampUserScale(next.userScale);

    const nextDisplayScale = computeDisplayScale(nextFitScale, clampedUserScale);

    const clamped = clampTranslate(

      viewport,

      map,

      nextDisplayScale,

      next.translateX,

      next.translateY

    );



    return {

      userScale: clampedUserScale,

      translateX: clamped.x,

      translateY: clamped.y,

    };

  }, []);



  const resetViewport = useCallback((options?: ViewportResetOptions) => {

    clearResetAnimation();

    // Same centered position the view opens with, not the raw (0,0) sentinel
    // — that would land on cover-fit's cropped axis pinned to its edge.
    setTransform(
      computeCenteredTransform(
        viewportSizeRef.current,
        mapSizeRef.current,
        INITIAL_TRANSFORM.userScale,
        fitModeRef.current
      )
    );

    setIsPanning(false);

    panStateRef.current = null;

    const animated = options?.animated ?? true;

    if (animated) {

      setIsResetAnimating(true);

      resetTimerRef.current = setTimeout(() => {

        resetTimerRef.current = null;

        setIsResetAnimating(false);

      }, VIEWPORT_RESET_TRANSITION_MS);

    }

  }, [clearResetAnimation]);



  const cancelPan = useCallback(() => {

    panStateRef.current = null;

    setIsPanning(false);

  }, []);



  useLayoutEffect(() => {

    if (!enabled) return;



    const element = viewportRef.current;

    if (!element) return;



    const syncViewportSize = (next: Size) => {

      setViewportSize((current) =>

        current.w === next.w && current.h === next.h ? current : next

      );

    };



    syncViewportSize(readViewportSize(element));



    const observer = new ResizeObserver((entries) => {

      const entry = entries[0];

      if (!entry) return;

      const { width, height } = entry.contentRect;

      syncViewportSize({ w: width, h: height });

    });



    observer.observe(element);

    return () => observer.disconnect();

  }, [enabled]);



  useEffect(() => {

    if (!enabled || viewportSize.w <= 0 || viewportSize.h <= 0) return;

    setTransform((current) => {
      // Only the untouched initial transform gets centered — once the user
      // has panned or zoomed, a later resize (window resize, sidebar
      // toggling) must reclamp their position, not recenter over it.
      const isUntouched =
        current.userScale === INITIAL_TRANSFORM.userScale &&
        current.translateX === INITIAL_TRANSFORM.translateX &&
        current.translateY === INITIAL_TRANSFORM.translateY;

      if (isUntouched) {
        return computeCenteredTransform(
          viewportSizeRef.current,
          mapSizeRef.current,
          INITIAL_TRANSFORM.userScale,
          fitModeRef.current
        );
      }

      return applyClampedTransform(current);
    });

  }, [applyClampedTransform, enabled, mapSize, viewportSize]);



  const previousFitModeRef = useRef(fitMode);

  useEffect(() => {
    // Toggling fit mode is a deliberate "show it the other way" action, not a
    // resize — it always snaps to the new mode's centered view, even if the
    // user had already panned around. The effect above only recenters an
    // untouched transform; it would otherwise reclamp a user's pan into the
    // new fit scale, landing somewhere arbitrary rather than the clean
    // centered view the toggle promises.
    if (previousFitModeRef.current === fitMode) return;
    previousFitModeRef.current = fitMode;

    if (!enabled) return;

    setTransform(
      computeCenteredTransform(
        viewportSizeRef.current,
        mapSizeRef.current,
        INITIAL_TRANSFORM.userScale,
        fitMode
      )
    );
  }, [enabled, fitMode]);



  useEffect(() => {

    if (!enabled) return;



    const element = viewportRef.current;

    if (!element) return;



    const handleWheel = (event: WheelEvent) => {

      event.preventDefault();

      clearResetAnimation();



      const rect = element.getBoundingClientRect();

      const cursor = {

        x: event.clientX - rect.left,

        y: event.clientY - rect.top,

      };



      setTransform((current) =>

        applyClampedTransform(

          zoomAtPoint(

            viewportSizeRef.current,

            mapSizeRef.current,

            current,

            cursor,

            event.deltaY,

            fitModeRef.current

          )

        )

      );

    };



    const handleMouseDown = (event: MouseEvent) => {

      if (!isMiddleMouseButton(event)) return;

      event.preventDefault();

      clearResetAnimation();



      const current = transformRef.current;

      panStateRef.current = {

        startClientX: event.clientX,

        startClientY: event.clientY,

        startTranslateX: current.translateX,

        startTranslateY: current.translateY,

      };

      setIsPanning(true);

    };



    const handleMouseMove = (event: MouseEvent) => {

      const panState = panStateRef.current;

      if (!panState) return;



      event.preventDefault();



      const deltaX = event.clientX - panState.startClientX;

      const deltaY = event.clientY - panState.startClientY;



      setTransform(

        applyClampedTransform({

          userScale: transformRef.current.userScale,

          translateX: panState.startTranslateX + deltaX,

          translateY: panState.startTranslateY + deltaY,

        })

      );

    };



    const endPanOnMouseUp = (event: MouseEvent) => {

      if (!panStateRef.current) return;

      if (!isMiddleMouseButton(event)) return;

      cancelPan();

    };



    const endPanOnLeave = () => {

      if (!panStateRef.current) return;

      cancelPan();

    };



    const endPanOnBlur = () => {

      if (!panStateRef.current) return;

      cancelPan();

    };



    const handleContextMenu = (event: MouseEvent) => {

      if (!panStateRef.current && event.button !== 1) return;

      event.preventDefault();

    };



    const handleAuxClick = (event: MouseEvent) => {

      if (event.button !== 1) return;

      event.preventDefault();

    };



    element.addEventListener("wheel", handleWheel, { passive: false });

    element.addEventListener("mousedown", handleMouseDown);

    element.addEventListener("mouseleave", endPanOnLeave);

    element.addEventListener("contextmenu", handleContextMenu);

    element.addEventListener("auxclick", handleAuxClick);

    window.addEventListener("mousemove", handleMouseMove);

    window.addEventListener("mouseup", endPanOnMouseUp);

    window.addEventListener("blur", endPanOnBlur);



    return () => {

      element.removeEventListener("wheel", handleWheel);

      element.removeEventListener("mousedown", handleMouseDown);

      element.removeEventListener("mouseleave", endPanOnLeave);

      element.removeEventListener("contextmenu", handleContextMenu);

      element.removeEventListener("auxclick", handleAuxClick);

      window.removeEventListener("mousemove", handleMouseMove);

      window.removeEventListener("mouseup", endPanOnMouseUp);

      window.removeEventListener("blur", endPanOnBlur);

    };

  }, [applyClampedTransform, cancelPan, clearResetAnimation, enabled]);



  useEffect(() => {

    return () => {

      if (resetTimerRef.current !== null) {

        clearTimeout(resetTimerRef.current);

      }

    };

  }, []);



  const screenToMapFromClient = useCallback(

    (clientX: number, clientY: number) => {

      const element = viewportRef.current;

      const viewport = viewportSizeRef.current;

      const map = mapSizeRef.current;

      const current = transformRef.current;

      const currentFitScale = computeFitScale(viewport, map, fitModeRef.current);

      const currentDisplayScale = computeDisplayScale(

        currentFitScale,

        current.userScale

      );



      if (!element || viewport.w <= 0 || viewport.h <= 0) return null;



      const rect = element.getBoundingClientRect();

      const viewportX = clientX - rect.left;

      const viewportY = clientY - rect.top;



      if (

        viewportX < 0 ||

        viewportY < 0 ||

        viewportX > viewport.w ||

        viewportY > viewport.h

      ) {

        return null;

      }



      const point = screenToMap(viewportX, viewportY, currentDisplayScale, {

        x: current.translateX,

        y: current.translateY,

      });



      if (point.x < 0 || point.y < 0 || point.x > map.w || point.y > map.h) {

        return null;

      }



      return point;

    },

    []

  );



  const transformStyle = viewportTransformStyle(

    displayScale,

    transform.translateX,

    transform.translateY

  );



  const cursorClassName = isPanning ? "cursor-grabbing" : "cursor-grab";

  const transformTransition =

    isResetAnimating && !isPanning ? VIEWPORT_RESET_TRANSITION : undefined;



  return {

    viewportRef,

    userScale: transform.userScale,

    translateX: transform.translateX,

    translateY: transform.translateY,

    displayScale,

    fitScale,

    isPanning,

    transformStyle,

    transformTransition,

    cursorClassName,

    resetViewport,

    screenToMapFromClient,

  };

}


