import asyncio
import json
from typing import Optional

from dotenv import load_dotenv
from fer import FER
from livekit import rtc
from livekit.agents import JobContext, WorkerOptions, cli

load_dotenv()


EMOTION_TOPIC = "emotion"  # data topic used by frontend


async def process_video_stream(
    ctx: JobContext,
    stream: rtc.VideoStream,
    participant_identity: str,
    min_change_score: float = 0.5,
    sample_every_n_frames: int = 5,
) -> None:
    """Read frames from a LiveKit VideoStream, run FER, and publish emotion
    changes as data messages to the room.
    """

    detector = FER(mtcnn=True)
    last_emotion: Optional[str] = None
    frame_idx = 0

    try:
        async for event in stream:
            frame_idx += 1
            if frame_idx % sample_every_n_frames != 0:
                continue

            frame = event.frame
            # Convert to RGB ndarray for FER
            img = frame.to_ndarray(format=rtc.VideoBufferType.RGB24)

            emotion, score = detector.top_emotion(img)
            if not emotion or score is None:
                continue

            # Only send if confident and changed
            if score >= min_change_score and emotion != last_emotion:
                last_emotion = emotion
                payload = {
                    "type": "emotion",
                    "identity": participant_identity,
                    "emotion": emotion,
                    "score": float(score),
                }
                await ctx.room.local_participant.publish_data(
                    json.dumps(payload),
                    reliable=True,
                    topic=EMOTION_TOPIC,
                )
    finally:
        await stream.aclose()


async def entrypoint(ctx: JobContext) -> None:
    """Agent that subscribes to video tracks in the room, runs FER,
    and publishes per-participant emotion over LiveKit data packets.
    """

    # Connect to the room. By default, remote tracks will be auto-subscribed.
    await ctx.connect()

    @ctx.room.on("track_subscribed")
    def on_track_subscribed(
        track: rtc.Track,
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ) -> None:
        if track.kind != rtc.TrackKind.KIND_VIDEO:
            return

        video_stream = rtc.VideoStream(track)
        asyncio.create_task(
            process_video_stream(ctx, video_stream, participant.identity),
            name=f"emotion-stream-{participant.identity}",
        )

    # Keep the agent process alive while the worker is running.
    await ctx.wait_forever()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
