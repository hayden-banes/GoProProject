from open_gopro import WiredGoPro, proto, Params
import asyncio

async def main ():
    async with WiredGoPro("4933") as gopro:
        print("Connected")

        try:
            # await gopro.http_setting.auto_off.set(Params.AutoOff.NEVER)
            # await gopro.http_command.load_preset_group(group=proto.EnumPresetGroup.PRESET_GROUP_ID_TIMELAPSE)

            await gopro.http_setting.media_format.set(Params.MediaFormat.TIME_LAPSE_PHOTO)
            await gopro.http_setting.fps.get_value()
            # print(response)
            # print(await gopro.http_command.get_camera_state())
        except Exception as e:
            print(repr(e))

asyncio.run(main())